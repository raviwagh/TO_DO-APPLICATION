"""Backup management utilities."""

import json
import shutil
from pathlib import Path
from datetime import datetime
from config.settings import TODO_FILE, BASE_DIR


class BackupManager:
    """Manages backup and restore of todo data."""
    
    BACKUP_DIR = BASE_DIR / "backups"
    MAX_BACKUPS = 10
    
    @classmethod
    def create_backup(cls) -> bool:
        """Create a backup of the current todos file."""
        try:
            # Create backup directory if it doesn't exist
            cls.BACKUP_DIR.mkdir(exist_ok=True)
            
            # Generate backup filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = cls.BACKUP_DIR / f"todos_backup_{timestamp}.json"
            
            # Copy current file to backup
            if Path(TODO_FILE).exists():
                shutil.copy2(TODO_FILE, backup_file)
                
                # Clean old backups
                cls._cleanup_old_backups()
                return True
            return False
        except Exception as e:
            print(f"Backup failed: {e}")
            return False
    
    @classmethod
    def _cleanup_old_backups(cls):
        """Keep only the most recent MAX_BACKUPS backups."""
        try:
            backups = sorted(cls.BACKUP_DIR.glob("todos_backup_*.json"), reverse=True)
            for old_backup in backups[cls.MAX_BACKUPS:]:
                old_backup.unlink()
        except Exception as e:
            print(f"Cleanup failed: {e}")
    
    @classmethod
    def list_backups(cls):
        """List all available backups."""
        try:
            cls.BACKUP_DIR.mkdir(exist_ok=True)
            backups = sorted(cls.BACKUP_DIR.glob("todos_backup_*.json"), reverse=True)
            return [(b.name, b.stat().st_mtime) for b in backups]
        except Exception as e:
            print(f"List backups failed: {e}")
            return []
    
    @classmethod
    def restore_backup(cls, backup_name: str) -> bool:
        """Restore from a specific backup."""
        try:
            backup_file = cls.BACKUP_DIR / backup_name
            if backup_file.exists():
                # Create a backup of current state before restoring
                cls.create_backup()
                
                # Restore the backup
                shutil.copy2(backup_file, TODO_FILE)
                return True
            return False
        except Exception as e:
            print(f"Restore failed: {e}")
            return False
    
    @classmethod
    def auto_backup(cls):
        """Create automatic backup (called periodically)."""
        return cls.create_backup()
