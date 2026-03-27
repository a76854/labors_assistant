"""
数据库初始化脚本
使用方法: python scripts/init_db.py
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.db.database import engine, Base, SessionLocal
from backend.db.models import Session, Message, CaseElement, Document, Template
from backend.config import get_settings

settings = get_settings()


def init_db():
    """初始化数据库"""
    print("📦 Initializing database...")
    
    # 创建所有表
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully!")
    
    # 初始化默认模板
    init_templates()
    
    print("✅ Database initialization complete!")


def init_templates():
    """初始化默认模板"""
    db = SessionLocal()
    
    templates = [
        {
            "id": "wage_arrears",
            "name": "拖欠工资诉状",
            "case_type": "wage_arrears",
            "description": "用于处理工资拖欠纠纷的诉状模板",
            "fields": ["plaintiff_name", "defendant_name", "salary_amount", "owed_months", "contract_start_date"],
            "example_content": "民事起诉状 - 拖欠工资纠纷范例"
        },
        {
            "id": "labor_contract",
            "name": "劳动合同纠纷诉状",
            "case_type": "labor_contract",
            "description": "用于处理劳动合同纠纷的诉状模板",
            "fields": ["plaintiff_name", "defendant_name", "contract_content", "dispute_details"],
            "example_content": "民事起诉状 - 劳动合同纠纷范例"
        },
        {
            "id": "work_injury",
            "name": "工伤赔偿诉状",
            "case_type": "work_injury",
            "description": "用于处理工伤赔偿纠纷的诉状模板",
            "fields": ["plaintiff_name", "defendant_name", "injury_date", "injury_description", "medical_expenses"],
            "example_content": "民事起诉状 - 工伤赔偿纠纷范例"
        }
    ]
    
    for template_data in templates:
        # 检查模板是否已存在
        existing = db.query(Template).filter(Template.id == template_data["id"]).first()
        if not existing:
            template = Template(**template_data)
            db.add(template)
            print(f"  ✓ Added template: {template_data['name']}")
        else:
            print(f"  ℹ Template already exists: {template_data['name']}")
    
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
