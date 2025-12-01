#!/usr/bin/env python3
"""
LensIQ Unused Code Cleanup Script

This script safely removes unused code from the LensIQ codebase based on
the comprehensive analysis. It includes safety checks and rollback capabilities.
"""

import os
import sys
import shutil
import logging
from pathlib import Path
from datetime import datetime
import subprocess
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class UnusedCodeCleaner:
    """Safe unused code removal with rollback capabilities."""
    
    def __init__(self, dry_run: bool = True):
        """Initialize the cleaner."""
        self.dry_run = dry_run
        self.backup_dir = Path(f"backup_unused_code_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        self.removed_files = []
        self.removed_dirs = []
        
        # Define unused code to remove
        self.unused_modules = [
            # Completely unused packages
            'src/analytics/',
            'src/regulatory/', 
            'src/backend/',
            
            # Unused individual files
            'src/ai/mcp_integration.py',
            'src/frontend/routes/main.py',
            
            # Development-only scripts
            'scripts/maintenance/',
            'scripts/populate_timeseries_data.py',
            'scripts/generate_additional_data.py',
            
            # Example files
            'examples/',
        ]
        
        # Files to check for import cleanup
        self.files_to_clean_imports = [
            'app.py',
            'src/backend/services/venture_signal_graph.py',
        ]
    
    def create_backup(self):
        """Create backup of files to be removed."""
        logger.info(f"Creating backup in {self.backup_dir}")
        
        if not self.dry_run:
            self.backup_dir.mkdir(exist_ok=True)
        
        for item in self.unused_modules:
            item_path = Path(item)
            if item_path.exists():
                backup_path = self.backup_dir / item
                
                if not self.dry_run:
                    backup_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    if item_path.is_dir():
                        shutil.copytree(item_path, backup_path)
                        logger.info(f"Backed up directory: {item}")
                    else:
                        shutil.copy2(item_path, backup_path)
                        logger.info(f"Backed up file: {item}")
                else:
                    logger.info(f"[DRY RUN] Would backup: {item}")
    
    def verify_unused_status(self, file_path: str) -> bool:
        """Verify that a file/module is actually unused."""
        logger.info(f"Verifying unused status of: {file_path}")
        
        # Get the module name for import checking
        if file_path.endswith('.py'):
            module_name = file_path.replace('/', '.').replace('.py', '')
            if module_name.startswith('src.'):
                module_name = module_name[4:]  # Remove 'src.' prefix
        else:
            # For directories, check the package name
            module_name = file_path.replace('/', '.').rstrip('/')
            if module_name.startswith('src.'):
                module_name = module_name[4:]
        
        # Search for imports of this module
        import_patterns = [
            f"from {module_name}",
            f"import {module_name}",
            f"from src.{module_name}",
            f"import src.{module_name}",
        ]
        
        # Search in all Python files
        python_files = list(Path('.').rglob('*.py'))
        
        for py_file in python_files:
            # Skip the file itself and backup directories
            if str(py_file).startswith(str(self.backup_dir)) or str(py_file) == file_path:
                continue
                
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                for pattern in import_patterns:
                    if pattern in content:
                        logger.warning(f"Found import of {module_name} in {py_file}")
                        return False
            except Exception as e:
                logger.warning(f"Could not read {py_file}: {e}")
        
        logger.info(f"Verified {file_path} is unused")
        return True
    
    def remove_unused_code(self):
        """Remove unused code files and directories."""
        logger.info("Starting unused code removal")
        
        for item in self.unused_modules:
            item_path = Path(item)
            
            if not item_path.exists():
                logger.info(f"Item does not exist: {item}")
                continue
            
            # Verify it's actually unused (skip for development scripts)
            if not item.startswith('scripts/') and not item.startswith('examples/'):
                if not self.verify_unused_status(item):
                    logger.error(f"Item appears to be used, skipping: {item}")
                    continue
            
            if self.dry_run:
                logger.info(f"[DRY RUN] Would remove: {item}")
                continue
            
            try:
                if item_path.is_dir():
                    shutil.rmtree(item_path)
                    self.removed_dirs.append(item)
                    logger.info(f"Removed directory: {item}")
                else:
                    item_path.unlink()
                    self.removed_files.append(item)
                    logger.info(f"Removed file: {item}")
            except Exception as e:
                logger.error(f"Failed to remove {item}: {e}")
    
    def clean_import_statements(self):
        """Clean up import statements in remaining files."""
        logger.info("Cleaning up import statements")
        
        # Import patterns to remove
        patterns_to_remove = [
            # Analytics imports
            "from src.analytics",
            "import src.analytics",
            "from .analytics",
            "get_advanced_esg_scorer",
            
            # Regulatory imports  
            "from src.regulatory",
            "import src.regulatory",
            "get_compliance_engine",
            
            # MCP imports
            "from src.ai.mcp_integration",
            "import src.ai.mcp_integration",
            
            # Backend service imports
            "from src.backend",
            "import src.backend",
        ]
        
        for file_path in self.files_to_clean_imports:
            file_path = Path(file_path)
            
            if not file_path.exists():
                continue
            
            logger.info(f"Cleaning imports in: {file_path}")
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                original_content = content
                lines = content.split('\n')
                cleaned_lines = []
                
                for line in lines:
                    # Check if line contains any pattern to remove
                    should_remove = False
                    for pattern in patterns_to_remove:
                        if pattern in line and (line.strip().startswith('from ') or 
                                              line.strip().startswith('import ') or
                                              line.strip().startswith('#')):
                            should_remove = True
                            break
                    
                    if not should_remove:
                        cleaned_lines.append(line)
                    elif not self.dry_run:
                        logger.info(f"Removed import line: {line.strip()}")
                
                cleaned_content = '\n'.join(cleaned_lines)
                
                if cleaned_content != original_content:
                    if not self.dry_run:
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(cleaned_content)
                        logger.info(f"Cleaned imports in: {file_path}")
                    else:
                        logger.info(f"[DRY RUN] Would clean imports in: {file_path}")
                
            except Exception as e:
                logger.error(f"Failed to clean imports in {file_path}: {e}")
    
    def update_app_imports(self):
        """Update app.py to remove unused import handling."""
        logger.info("Updating app.py imports")
        
        app_file = Path('app.py')
        if not app_file.exists():
            return
        
        try:
            with open(app_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Remove try/except blocks for unused imports
            lines = content.split('\n')
            cleaned_lines = []
            skip_block = False
            
            for line in lines:
                # Check for try blocks importing unused modules
                if ('try:' in line and 
                    any(pattern in content[content.find(line):content.find(line) + 200] 
                        for pattern in ['analytics', 'regulatory', 'mcp_integration'])):
                    skip_block = True
                    continue
                
                # Skip until we find the except block end
                if skip_block:
                    if line.strip().startswith('except'):
                        continue
                    elif line.strip() == '' or line.startswith('    '):
                        continue
                    else:
                        skip_block = False
                
                if not skip_block:
                    cleaned_lines.append(line)
            
            cleaned_content = '\n'.join(cleaned_lines)
            
            if not self.dry_run and cleaned_content != content:
                with open(app_file, 'w', encoding='utf-8') as f:
                    f.write(cleaned_content)
                logger.info("Updated app.py imports")
            elif self.dry_run:
                logger.info("[DRY RUN] Would update app.py imports")
                
        except Exception as e:
            logger.error(f"Failed to update app.py: {e}")
    
    def test_application(self) -> bool:
        """Test that the application still works after cleanup."""
        logger.info("Testing application after cleanup")
        
        try:
            # Try to import the main app
            result = subprocess.run([
                sys.executable, '-c', 
                'from app import app; print("App import successful")'
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                logger.info("Application import test passed")
                return True
            else:
                logger.error(f"Application import test failed: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("Application test timed out")
            return False
        except Exception as e:
            logger.error(f"Application test failed: {e}")
            return False
    
    def create_rollback_script(self):
        """Create a rollback script to restore removed code."""
        rollback_script = Path('rollback_cleanup.py')
        
        script_content = f'''#!/usr/bin/env python3
"""
Rollback script for unused code cleanup.
Generated on: {datetime.now().isoformat()}
"""

import shutil
from pathlib import Path

def rollback():
    """Restore removed files from backup."""
    backup_dir = Path("{self.backup_dir}")
    
    if not backup_dir.exists():
        print("Backup directory not found!")
        return False
    
    print("Restoring files from backup...")
    
    # Restore removed files
    removed_files = {self.removed_files}
    removed_dirs = {self.removed_dirs}
    
    for item in removed_files + removed_dirs:
        backup_path = backup_dir / item
        restore_path = Path(item)
        
        if backup_path.exists():
            if backup_path.is_dir():
                shutil.copytree(backup_path, restore_path, dirs_exist_ok=True)
            else:
                restore_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(backup_path, restore_path)
            print(f"Restored: {{item}}")
    
    print("Rollback completed!")
    return True

if __name__ == '__main__':
    rollback()
'''
        
        if not self.dry_run:
            with open(rollback_script, 'w') as f:
                f.write(script_content)
            rollback_script.chmod(0o755)
            logger.info(f"Created rollback script: {rollback_script}")
        else:
            logger.info(f"[DRY RUN] Would create rollback script: {rollback_script}")
    
    def generate_cleanup_report(self):
        """Generate a report of what was cleaned up."""
        report = {
            'timestamp': datetime.now().isoformat(),
            'dry_run': self.dry_run,
            'removed_files': self.removed_files,
            'removed_directories': self.removed_dirs,
            'backup_location': str(self.backup_dir),
            'total_items_removed': len(self.removed_files) + len(self.removed_dirs)
        }
        
        report_file = Path('cleanup_report.json')
        
        if not self.dry_run:
            with open(report_file, 'w') as f:
                json.dump(report, f, indent=2)
            logger.info(f"Generated cleanup report: {report_file}")
        else:
            logger.info(f"[DRY RUN] Would generate cleanup report: {report_file}")
        
        return report
    
    def run_cleanup(self):
        """Run the complete cleanup process."""
        logger.info(f"Starting unused code cleanup (dry_run={self.dry_run})")
        
        try:
            # Step 1: Create backup
            self.create_backup()
            
            # Step 2: Remove unused code
            self.remove_unused_code()
            
            # Step 3: Clean import statements
            self.clean_import_statements()
            
            # Step 4: Update app.py
            self.update_app_imports()
            
            # Step 5: Test application (only if not dry run)
            if not self.dry_run:
                if not self.test_application():
                    logger.error("Application test failed! Consider rollback.")
                    return False
            
            # Step 6: Create rollback script
            self.create_rollback_script()
            
            # Step 7: Generate report
            report = self.generate_cleanup_report()
            
            logger.info("Cleanup completed successfully!")
            logger.info(f"Removed {report['total_items_removed']} items")
            
            if not self.dry_run:
                logger.info(f"Backup created at: {self.backup_dir}")
                logger.info("Run 'python rollback_cleanup.py' to restore if needed")
            
            return True
            
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")
            return False


def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Clean up unused code from LensIQ')
    parser.add_argument('--dry-run', action='store_true', 
                       help='Show what would be removed without actually removing')
    parser.add_argument('--force', action='store_true',
                       help='Actually perform the cleanup')
    
    args = parser.parse_args()
    
    if not args.force and not args.dry_run:
        print("Use --dry-run to see what would be removed, or --force to actually remove")
        return
    
    cleaner = UnusedCodeCleaner(dry_run=not args.force)
    success = cleaner.run_cleanup()
    
    if success:
        print("Cleanup completed successfully!")
    else:
        print("Cleanup failed!")
        sys.exit(1)


if __name__ == '__main__':
    main()
