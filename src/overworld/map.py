# ABOUTME: Map manager for TMX maps with cached rendering surfaces
# ABOUTME: Handles collisions, grass detection, and object-driven spawns

from __future__ import annotations

import os
from typing import Any

import pygame
import pytmx

from src.engine import constants
from src.overworld.dialog_loader import DialogLoader
from src.overworld.item_pickup import ItemPickup
from src.overworld.npc import NPC


class MapManager:
    """Loads TMX maps, caches render surfaces, and exposes map helpers."""

    def __init__(self, map_filepath: str):
        self.map_filepath = map_filepath
        self.map_name = os.path.splitext(os.path.basename(map_filepath))[0]
        self.tmx_data = pytmx.load_pygame(map_filepath)

        self.width = self.tmx_data.width       # Map width in base tiles
        self.height = self.tmx_data.height     # Map height in base tiles
        self.tile_width = self.tmx_data.tilewidth
        self.tile_height = self.tmx_data.tileheight

        if self.tile_width != constants.TILE_SIZE or self.tile_height != constants.TILE_SIZE:
            raise ValueError(
                f"TMX tile size {self.tile_width}x{self.tile_height} "
                f"does not match TILE_SIZE={constants.TILE_SIZE}"
            )

        # Map dimensions in metatiles (for collision/movement grid)
        self.metatile_width = self.width // 2
        self.metatile_height = self.height // 2

        self.lower_layers: list[pytmx.TiledTileLayer] = []
        self.fringe_layers: list[pytmx.TiledTileLayer] = []
        self._collect_layers()

        # Collision grids are on metatile grid (16x16), not base tile grid (8x8)
        self._solid_grid = [[False for _ in range(self.metatile_width)] for _ in range(self.metatile_height)]
        self._grass_grid = [[False for _ in range(self.metatile_width)] for _ in range(self.metatile_height)]
        self._build_collision_and_grass()

        self.lower_surface: pygame.Surface
        self.fringe_surface: pygame.Surface
        self._build_cached_surfaces()

        self.npcs: list[NPC] = []
        self.warps: list[dict[str, Any]] = []
        self.item_pickups: list[ItemPickup] = []
        self.player_start: tuple[int, int] | None = None
        self.dialog_loader = DialogLoader()
        self._parse_objects()
        self._build_tile_warps()

    def _collect_layers(self) -> None:
        for layer in self.tmx_data.layers:
            if not isinstance(layer, pytmx.TiledTileLayer):
                continue
            if not layer.visible:
                continue
            if self._is_collision_layer(layer):
                continue
            if self._is_fringe_layer(layer):
                self.fringe_layers.append(layer)
            else:
                self.lower_layers.append(layer)

    def _is_collision_layer(self, layer: pytmx.TiledTileLayer) -> bool:
        name = (layer.name or "").lower()
        return "collision" in name

    def _is_fringe_layer(self, layer: pytmx.TiledTileLayer) -> bool:
        name = (layer.name or "").lower()
        if layer.properties.get("fringe"):
            return True
        if layer.properties.get("layer_type") == "fringe":
            return True
        return any(tag in name for tag in ("fringe", "upper", "top", "above", "roof"))

    def _build_collision_and_grass(self) -> None:
        # Build collision on metatile grid (16x16), aggregating 2x2 base tiles
        # A metatile is solid if ANY of its 4 base tiles are solid
        # A metatile is grass if ANY of its 4 base tiles are grass
        for metatile_y in range(self.metatile_height):
            for metatile_x in range(self.metatile_width):
                base_x = metatile_x * 2
                base_y = metatile_y * 2

                # Check all 4 base tiles in this metatile
                for dy in range(2):
                    for dx in range(2):
                        tile_x = base_x + dx
                        tile_y = base_y + dy

                        # Check all layers for this tile position
                        for layer in self.tmx_data.layers:
                            if not isinstance(layer, pytmx.TiledTileLayer):
                                continue
                            gid = layer.data[tile_y][tile_x] if tile_y < len(layer.data) and tile_x < len(layer.data[tile_y]) else 0
                            if gid == 0:
                                continue
                            properties = self.tmx_data.get_tile_properties_by_gid(gid) or {}
                            if "solid" in properties:
                                self._solid_grid[metatile_y][metatile_x] = True
                            if "is_grass" in properties:
                                self._grass_grid[metatile_y][metatile_x] = True

    def _build_cached_surfaces(self) -> None:
        width_px = self.width * self.tile_width
        height_px = self.height * self.tile_height
        self.lower_surface = pygame.Surface((width_px, height_px))
        self.fringe_surface = pygame.Surface((width_px, height_px), pygame.SRCALPHA)

        self._render_layers_to_surface(self.lower_layers, self.lower_surface)
        self._render_layers_to_surface(self.fringe_layers, self.fringe_surface)

    def _render_layers_to_surface(
        self,
        layers: list[pytmx.TiledTileLayer],
        surface: pygame.Surface
    ) -> None:
        for layer in layers:
            for x, y, gid in layer:
                if gid == 0:
                    continue
                tile = self.tmx_data.get_tile_image_by_gid(gid)
                if tile:
                    # Tiled anchors larger tiles at the bottom, so adjust Y for tiles
                    # taller than the map's base tile size
                    tile_height = tile.get_height()
                    y_offset = tile_height - self.tile_height
                    px = x * self.tile_width
                    py = y * self.tile_height - y_offset
                    surface.blit(tile, (px, py))

    def _parse_objects(self) -> None:
        for obj in self.tmx_data.objects:
            obj_type = (obj.type or "").strip().lower()
            if not obj_type:
                continue
            if obj_type == "npc":
                self._spawn_npc(obj)
            elif obj_type == "warp":
                self._register_warp(obj)
            elif obj_type == "item":
                self._spawn_item(obj)

    def _spawn_npc(self, obj: pytmx.TiledObject) -> None:
        npc_id = obj.properties.get("npc_id") or obj.name or f"npc_{len(self.npcs) + 1}"
        direction = obj.properties.get("direction", "down")
        dialog_id = obj.properties.get("dialog_id")
        dialog_text = self.dialog_loader.get_dialog(dialog_id) if dialog_id else "..."
        tile_x, tile_y = self._object_tile_position(obj)
        sprite_id = obj.properties.get("sprite_id")

        is_trainer = bool(obj.properties.get("is_trainer"))
        trainer_data = None
        if is_trainer:
            trainer_data = {
                "name": obj.properties.get("trainer_name", "Trainer"),
                "class": obj.properties.get("trainer_class", "Trainer"),
                "team": self._parse_team(obj.properties.get("team")),
                "prize_money": self._coerce_int(obj.properties.get("prize_money"), 0)
            }

        self.npcs.append(NPC(
            npc_id, tile_x, tile_y,
            direction=direction,
            dialog_text=dialog_text,
            is_trainer=is_trainer,
            trainer_data=trainer_data,
            sprite_id=sprite_id
        ))

    def _spawn_item(self, obj: pytmx.TiledObject) -> None:
        item_id = obj.properties.get("item_id")
        if not item_id:
            return
        pickup_id = obj.properties.get("pickup_id") or obj.name or f"item_{len(self.item_pickups) + 1}"
        tile_x, tile_y = self._object_tile_position(obj)
        self.item_pickups.append(ItemPickup(pickup_id, item_id, tile_x, tile_y))

    def _register_warp(self, obj: pytmx.TiledObject) -> None:
        dest_map = obj.properties.get("dest_map")
        if not dest_map:
            return
        dest_x = self._coerce_int(obj.properties.get("dest_x"), 0)
        dest_y = self._coerce_int(obj.properties.get("dest_y"), 0)
        # Calculate warp bounds in metatile coordinates
        min_tile_x = int(obj.x // constants.METATILE_SIZE)
        max_tile_x = int((obj.x + obj.width - 1) // constants.METATILE_SIZE)
        min_tile_y = int(obj.y // constants.METATILE_SIZE)
        max_tile_y = int((obj.y + obj.height - 1) // constants.METATILE_SIZE)
        self.warps.append({
            "min_tile_x": min_tile_x,
            "max_tile_x": max_tile_x,
            "min_tile_y": min_tile_y,
            "max_tile_y": max_tile_y,
            "dest_map": dest_map,
            "dest_x": dest_x,
            "dest_y": dest_y
        })

    def _object_tile_position(self, obj: pytmx.TiledObject) -> tuple[int, int]:
        """Convert pixel position to metatile position."""
        metatile_x = int(obj.x // constants.METATILE_SIZE)
        metatile_y = int(obj.y // constants.METATILE_SIZE)
        return metatile_x, metatile_y

    def _coerce_int(self, value: Any, default: int) -> int:
        if value is None:
            return default
        try:
            return int(value)
        except (TypeError, ValueError):
            return default

    def _parse_team(self, team_str: Any) -> list:
        """Parse team from JSON string or return empty list."""
        if not team_str:
            return []
        if isinstance(team_str, list):
            return team_str
        try:
            import json
            return json.loads(team_str)
        except (json.JSONDecodeError, TypeError):
            return []

    def _is_truthy(self, value: Any) -> bool:
        if value is None:
            return False
        if isinstance(value, str):
            lower = value.strip().lower()
            if lower in ("false", "0", "no"):
                return False
            # Empty string or any other string value means property is set
            return True
        return bool(value)

    def _build_tile_warps(self) -> None:
        """Scan tiles for entry/playerStart properties (pylletTown format)."""
        for layer in self.tmx_data.layers:
            if not isinstance(layer, pytmx.TiledTileLayer):
                continue
            for x, y, gid in layer:
                if gid == 0:
                    continue
                properties = self.tmx_data.get_tile_properties_by_gid(gid) or {}
                entry = properties.get("entry")
                if entry:
                    # Convert base tile to metatile coordinates
                    metatile_x = x // 2
                    metatile_y = y // 2
                    self.warps.append({
                        "min_tile_x": metatile_x,
                        "max_tile_x": metatile_x,
                        "min_tile_y": metatile_y,
                        "max_tile_y": metatile_y,
                        "dest_map": entry,
                        "dest_x": -1,  # -1 means use destination map's playerStart
                        "dest_y": -1
                    })
                player_start = properties.get("playerStart")
                if player_start and self.player_start is None:
                    # Convert base tile to metatile coordinates
                    self.player_start = (x // 2, y // 2)


    def draw_base(self, renderer, camera_x: int, camera_y: int) -> None:
        renderer.draw_surface(self.lower_surface, (-camera_x, -camera_y))

    def draw_fringe(self, renderer, camera_x: int, camera_y: int) -> None:
        renderer.draw_surface(self.fringe_surface, (-camera_x, -camera_y))

    def is_walkable(self, metatile_x: int, metatile_y: int) -> bool:
        """Check if metatile position is walkable."""
        if metatile_x < 0 or metatile_x >= self.metatile_width:
            return False
        if metatile_y < 0 or metatile_y >= self.metatile_height:
            return False
        return not self._solid_grid[metatile_y][metatile_x]

    def is_grass(self, metatile_x: int, metatile_y: int) -> bool:
        """Check if metatile position is grass."""
        if metatile_x < 0 or metatile_x >= self.metatile_width:
            return False
        if metatile_y < 0 or metatile_y >= self.metatile_height:
            return False
        return self._grass_grid[metatile_y][metatile_x]

    def get_warp_at(self, tile_x: int, tile_y: int) -> dict[str, Any] | None:
        for warp in self.warps:
            if (warp["min_tile_x"] <= tile_x <= warp["max_tile_x"] and
                warp["min_tile_y"] <= tile_y <= warp["max_tile_y"]):
                return warp
        return None

    def get_width_pixels(self) -> int:
        return self.width * self.tile_width

    def get_height_pixels(self) -> int:
        return self.height * self.tile_height
