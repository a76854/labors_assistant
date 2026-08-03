"""
数据库初始化脚本
使用方法: python scripts/init_db.py
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text

from backend.db.database import engine, Base, SessionLocal
from backend.db.models import Session, Message, CaseElement, Document, Template, User, Lead, MaterialRequest
from backend.config import get_settings
from backend.services.auth import hash_password

settings = get_settings()

# 地区模板定义: 3 案由 × 3 地区
REGIONS = [
    {
        "key": "beijing",
        "name": "北京",
        "institution": "北京市朝阳区劳动人事争议仲裁委员会",
    },
    {
        "key": "shanghai",
        "name": "上海",
        "institution": "上海市劳动人事争议仲裁委员会",
    },
    {
        "key": "guangdong",
        "name": "广东",
        "institution": "广东省劳动人事争议仲裁委员会",
    },
]

CASE_TYPES = [
    {
        "key": "wage_arrears",
        "name": "拖欠工资",
        "fields": ["plaintiff_name", "defendant_name", "salary_amount", "owed_months", "contract_start_date"],
    },
    {
        "key": "labor_contract",
        "name": "劳动合同纠纷",
        "fields": ["plaintiff_name", "defendant_name", "contract_content", "dispute_details"],
    },
    {
        "key": "work_injury",
        "name": "工伤赔偿",
        "fields": ["plaintiff_name", "defendant_name", "injury_date", "injury_description", "medical_expenses"],
    },
]


def init_db():
    """初始化数据库"""
    print("📦 Initializing database...")
    
    # 创建所有表
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully!")
    
    # 轻量迁移：为已有表补充新列（SQLite 无原生 ALTER 迁移工具）
    migrate_columns()
    
    # 初始化默认模板（按地区）
    init_templates()
    
    # 初始化演示账号
    init_demo_users()
    
    print("✅ Database initialization complete!")


def migrate_columns():
    """轻量迁移：若列不存在则补充。"""
    checks = [
        ("sessions", "region", "VARCHAR(50)"),
        ("templates", "region", "VARCHAR(50)"),
    ]
    with engine.begin() as conn:
        for table, column, col_type in checks:
            rows = conn.execute(text(f"PRAGMA table_info({table})")).fetchall()
            exists = any(row[1] == column for row in rows)
            if not exists:
                conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {column} {col_type}"))
                print(f"  ➕ Migrated: {table}.{column}")
            else:
                print(f"  ℹ Column exists: {table}.{column}")


def init_templates():
    """初始化默认模板（3 案由 × 3 地区，共 9 条）"""
    db = SessionLocal()

    # 清理旧版无地区的模板
    old_templates = db.query(Template).filter(
        (Template.region.is_(None)) | (Template.region == "")
    ).all()
    for old in old_templates:
        db.delete(old)
        print(f"  🗑  Removed legacy template: {old.id}")

    for region in REGIONS:
        for case_type in CASE_TYPES:
            template_id = f"{case_type['key']}_{region['key']}"
            existing = db.query(Template).filter(Template.id == template_id).first()
            if existing:
                print(f"  ℹ Template exists: {template_id}")
                continue

            template = Template(
                id=template_id,
                name=f"{region['name']}·{case_type['name']}诉状",
                case_type=case_type["key"],
                region=region["key"],
                description=(
                    f"适用于{region['name']}地区的{case_type['name']}纠纷，"
                    f"受理机构：{region['institution']}。"
                ),
                fields=case_type["fields"],
                example_content=(
                    f"民事起诉状 - {case_type['name']}范例（{region['name']}）\n"
                    f"受理机构：{region['institution']}"
                ),
            )
            db.add(template)
            print(f"  ✓ Added template: {template.id}")

    db.commit()
    db.close()


def init_demo_users():
    """初始化演示账号（便于比赛演示）"""
    db = SessionLocal()

    demo_users = [
        {
            "username": "lawyer_demo",
            "password": "demo123456",
            "role": "lawyer",
            "name": "陈志远（演示律师）",
            "phone": "13800138000",
        },
        {
            "username": "worker_demo",
            "password": "demo123456",
            "role": "user",
            "name": "演示劳动者",
            "phone": "13900139000",
        },
    ]

    # 10 个假律师账号（演示用）
    fake_lawyer_names = [
        ("lawyer01", "陈志远", "13800138001"),
        ("lawyer02", "李婉晴", "13800138002"),
        ("lawyer03", "王建国", "13800138003"),
        ("lawyer04", "赵敏", "13800138004"),
        ("lawyer05", "孙德胜", "13800138005"),
        ("lawyer06", "周静", "13800138006"),
        ("lawyer07", "吴振华", "13800138007"),
        ("lawyer08", "郑丽娜", "13800138008"),
        ("lawyer09", "钱永强", "13800138009"),
        ("lawyer10", "冯雪", "13800138010"),
    ]
    for username, name, phone in fake_lawyer_names:
        demo_users.append({
            "username": username,
            "password": "demo123456",
            "role": "lawyer",
            "name": f"{name}（律师）",
            "phone": phone,
        })

    for data in demo_users:
        existing = db.query(User).filter(User.username == data["username"]).first()
        if existing:
            print(f"  ℹ Demo user exists: {data['username']}")
            continue
        user = User(
            username=data["username"],
            password_hash=hash_password(data["password"]),
            role=data["role"],
            name=data["name"],
            phone=data["phone"],
        )
        db.add(user)
        print(f"  ✓ Added demo user: {data['username']} ({data['role']})")

    db.commit()
    db.close()


def drop_db():
    """删除所有表（谨慎使用）"""
    print("⚠️  Dropping all tables...")
    Base.metadata.drop_all(bind=engine)
    print("✅ All tables dropped!")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Database initialization script")
    parser.add_argument("--reset", action="store_true", help="Reset database (drop all tables)")
    args = parser.parse_args()
    
    if args.reset:
        drop_db()
        print()
    
    init_db()
