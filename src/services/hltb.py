from typing import Any, Callable, Dict

from fastapi import status
from howlongtobeatpy import HowLongToBeat, HowLongToBeatEntry

from utils.custom_errors import HTTPError

Mapper = Callable[[HowLongToBeatEntry], Dict[str, Any]]


class HltbService:
    service: HowLongToBeat

    def __init__(self: HltbService):
        self.service = HowLongToBeat()

    def getMapper(self: HltbService, mode: str):
        mappers: Dict[str, Mapper] = {
            "options": lambda entry: {
                "name": entry.game_name,
                "id": str(entry.game_id),
            },
            "info": lambda entry: {
                "name": entry.game_name,
                "show_combine": entry.json_content["comp_lvl_combine"],
                "show_solo": entry.json_content["comp_lvl_sp"],
                "show_coop": entry.json_content["comp_lvl_co"],
                "show_mp": entry.json_content["comp_lvl_mp"],
                "main": entry.main_story,
                "main_extra": entry.main_extra,
                "completionist": entry.completionist,
                "coop": entry.coop_time,
                "multiplayer": entry.mp_time,
            },
        }
        if mode not in mappers:
            raise HTTPError(
                status_code=status.HTTP_400_BAD_REQUEST,
                message=f"Unknown mode '{mode}'",
            )
        return mappers[mode]

    def parseTime(self: HltbService, time: str):
        timeFloat = float(time)
        if timeFloat == 0:
            return None
        hour = int(timeFloat)
        frac = timeFloat - hour

        if frac <= 0.30:
            return float(hour)
        elif frac >= 0.70:
            return float(hour + 1)
        else:
            return hour + 0.5

    def parseData(self: HltbService, info: Dict):
        info = {
            **info,
            "main": self.parseTime(info.get("main", None)),
            "main_extra": self.parseTime(info.get("main_extra", None)),
            "completionist": self.parseTime(info.get("completionist", None)),
            "coop": self.parseTime(info.get("coop", None)),
            "multiplayer": self.parseTime(info.get("multiplayer", None)),
            "singleplayer": None,
        }

        if not info.get("show_coop", False):
            info["coop"] = None
        info.pop("show_coop", None)

        if not info.get("show_mp", False):
            info["multiplayer"]
        info.pop("show_mp", None)

        if info.get("show_solo", False):
            if info.get("show_combine", True):
                values = [
                    info.get(k, 0) for k in ["main", "main_extra", "completionist"]
                ]
                info["singleplayer"] = [min(values), max(values)]
            else:
                info["coop"] = info["multiplayer"] = None
        if info.get("show_combine", False) or not info.get("show_solo", False):
            info["main"] = info["main_extra"] = info["completionist"] = None
        info.pop("show_combine", None)
        info.pop("show_solo", None)

        return info

    async def getOptions(self: HltbService, name: str):
        try:
            map_options = self.getMapper("options")
            return list(map(map_options, await self.service.async_search(name)))
        except Exception as _:
            return []

    async def getInfo(self: HltbService, id: str):
        try:
            map_info = self.getMapper("info")
            return self.parseData(map_info(await self.service.async_search_from_id(id)))
        except Exception as _:
            raise HTTPError(
                status_code=status.HTTP_404_NOT_FOUND, message="Game not found"
            )

    async def handle(self: HltbService, method: str, query: dict):
        methodMap: Dict[str, Callable] = {
            "options": self.getOptions,
            "info": self.getInfo,
        }

        if method not in methodMap:
            raise HTTPError(
                status_code=status.HTTP_400_BAD_REQUEST,
                message="Invalid endpoint! Use /[options|info]",
            )

        try:
            param = query["name" if method == "options" else "id"]
        except Exception as _:
            raise HTTPError(
                status_code=status.HTTP_400_BAD_REQUEST,
                message=f"Missing parameter for the {method} endpoint",
            )

        return await methodMap[method](param)
