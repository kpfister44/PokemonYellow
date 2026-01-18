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

        self.width = self.tmx_data.width
        self.height = self.tmx_data.height
        self.tile_width = self.tmx_data.tilewidth
        self.tile_height = self.tmx_data.tileheight

        if self.tile_width != constants.TILE_SIZE or self.tile_height != constants.TILE_SIZE:
            raise ValueError(
                f"TMX tile size {self.tile_width}x{self.tile_height} "
                f"does not match TILE_SIZE={constants.TILE_SIZE}"
            )

        self.lower_layers: list[pytmx.TiledTileLayer] = []
        self.fringe_layers: list[pytmx.TiledTileLayer] = []
        self._collect_layers()

        self._solid_grid = [[False for _ in range(self.width)] for _ in range(self.height)]
        self._grass_grid = [[False for _ in range(self.width)] for _ in range(self.height)]
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
        for layer in self.tmx_data.layers:
            if not isinstance(layer, pytmx.TiledTileLayer):
                continue
            for x, y, gid in layer:
                if gid == 0:
                    continue
                properties = self.tmx_data.get_tile_properties_by_gid(gid) or {}
                if self._is_truthy(properties.get("solid")):
                    self._solid_grid[y][x] = True
                if self._is_truthy(properties.get("is_grass")):
                    self._grass_grid[y][x] = True

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
                    surface.blit(tile, (x * self.tile_width, y * self.tile_height))

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
        self.npcs.append(NPC(npc_id, tile_x, tile_y, direction=direction, dialog_text=dialog_text))

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
        tile_x, tile_y = self._object_tile_position(obj)
        self.warps.append({
            "tile_x": tile_x,
            "tile_y": tile_y,
            "dest_map": dest_map,
            "dest_x": dest_x,
            "dest_y": dest_y
        })

    def _object_tile_position(self, obj: pytmx.TiledObject) -> tuple[int, int]:
        tile_x = int(obj.x // self.tile_width)
        tile_y = int(obj.y // self.tile_height)
        return tile_x, tile_y

    def _coerce_int(self, value: Any, default: int) -> int:
        if value is None:
            return default
        try:
            return int(value)
        except (TypeError, ValueError):
            return default

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
                    self.warps.append({
                        "tile_x": x,
                        "tile_y": y,
                        "dest_map": entry,
                        "dest_x": 0,
                        "dest_y": 0
                    })
                player_start = properties.get("playerStart")
                if player_start and self.player_start is None:
                    self.player_start = (x, y)

    def draw_base(self, renderer, camera_x: int, camera_y: int) -> None:
        renderer.draw_surface(self.lower_surface, (-camera_x, -camera_y))

    def draw_fringe(self, renderer, camera_x: int, camera_y: int) -> None:
        renderer.draw_surface(self.fringe_surface, (-camera_x, -camera_y))

    def is_walkable(self, tile_x: int, tile_y: int) -> bool:
        if tile_x < 0 or tile_x >= self.width or tile_y < 0 or tile_y >= self.height:
            return False
        return not self._solid_grid[tile_y][tile_x]

    def is_grass(self, tile_x: int, tile_y: int) -> bool:
        if tile_x < 0 or tile_x >= self.width or tile_y < 0 or tile_y >= self.height:
            return False
        return self._grass_grid[tile_y][tile_x]

    def get_warp_at(self, tile_x: int, tile_y: int) -> dict[str, Any] | None:
        for warp in self.warps:
            if warp["tile_x"] == tile_x and warp["tile_y"] == tile_y:
                return warp
        return None

    def get_width_pixels(self) -> int:
        return self.width * self.tile_width

    def get_height_pixels(self) -> int:
        return self.height * self.tile_height
