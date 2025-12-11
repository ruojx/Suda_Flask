# reset_db.py - 最彻底的清空方式（删除所有表并重新创建）
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db

app = create_app()

def reset_database():
    """重置数据库（删除所有表并重新创建）"""
    with app.app_context():
        print("=" * 60)
        print("⚠️  WARNING: This will DROP ALL TABLES and recreate them!")
        print("=" * 60)
        
        confirm = input("Type 'RESET_DB' to confirm: ")
        
        if confirm != 'RESET_DB':
            print("Operation cancelled.")
            return
        
        print("Resetting database...")
        
        try:
            # 删除所有表
            db.drop_all()
            print("✓ Dropped all tables")
            
            # 重新创建所有表
            db.create_all()
            print("✓ Created all tables")
            
            print("=" * 60)
            print("✅ Database reset successfully!")
            print("=" * 60)
            
        except Exception as e:
            print(f"❌ Error resetting database: {e}")

if __name__ == '__main__':
    reset_database()