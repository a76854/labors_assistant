"""
地区规则适配 - 地区与仲裁机构映射

不同地区仲裁材料与格式存在差异，模板按地区切换。
"""

from typing import Dict, List

REGIONS: List[Dict[str, str]] = [
    {
        "key": "beijing",
        "name": "北京",
        "institution": "北京市朝阳区劳动人事争议仲裁委员会",
        "note": "劳动争议须先经劳动仲裁；仲裁申请书一式两份，格式按《北京市劳动人事争议仲裁文书模板》",
    },
    {
        "key": "shanghai",
        "name": "上海",
        "institution": "上海市劳动人事争议仲裁委员会",
        "note": "上海实行仲裁前置；仲裁申请书需注明劳动争议发生地及劳动合同履行地",
    },
    {
        "key": "guangdong",
        "name": "广东",
        "institution": "广东省劳动人事争议仲裁委员会",
        "note": "广东部分地区实行劳动争议调解前置程序，申请仲裁前可先行申请调解",
    },
]

REGION_MAP: Dict[str, Dict[str, str]] = {region["key"]: region for region in REGIONS}


def get_region_info(region: str | None) -> Dict[str, str]:
    """获取地区信息，未知地区回退北京。"""
    return REGION_MAP.get(region or "beijing", REGION_MAP["beijing"])


def get_institution(region: str | None) -> str:
    """获取地区仲裁/管辖机构名称。"""
    return get_region_info(region)["institution"]


def get_regions() -> List[Dict[str, str]]:
    """返回全部地区列表。"""
    return REGIONS
