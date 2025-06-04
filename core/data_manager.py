import json
import pandas as pd
import os
from pathlib import Path
import time

class DataManager:
    """Handles data saving, loading, and management operations"""
    
    def __init__(self, base_output_dir="output"):
        """
        Initialize DataManager with output directory structure
        
        Args:
            base_output_dir: Base directory for all output files
        """
        self.base_output_dir = base_output_dir
        self.json_dir = os.path.join(base_output_dir, "json")
        self.csv_dir = os.path.join(base_output_dir, "csv")
        self.ensure_output_dirs()
    
    def ensure_output_dirs(self):
        """Create output directories if they don't exist"""
        Path(self.json_dir).mkdir(parents=True, exist_ok=True)
        Path(self.csv_dir).mkdir(parents=True, exist_ok=True)
    
    def save_to_csv(self, data, filename=None):
        """
        Save scraped data to CSV
        
        Args:
            data: List of dictionaries containing product data
            filename: Optional custom filename, if None uses timestamp
        """
        if not data:
            print("No data to save")
            return None
            
        if filename is None:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"tokopedia_products_{timestamp}.csv"
        
        # Ensure .csv extension
        if not filename.endswith('.csv'):
            filename += '.csv'
            
        filepath = os.path.join(self.csv_dir, filename)
        
        try:
            df = pd.DataFrame(data)
            df.to_csv(filepath, index=False, encoding='utf-8')
            print(f"Data saved to {filepath}")
            return filepath
        except Exception as e:
            print(f"Error saving CSV: {str(e)}")
            return None
    
    def save_to_json(self, data, filename=None):
        """
        Save scraped data to JSON
        
        Args:
            data: List of dictionaries containing product data
            filename: Optional custom filename, if None uses timestamp
        """
        if not data:
            print("No data to save")
            return None
            
        if filename is None:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"tokopedia_products_{timestamp}.json"
        
        # Ensure .json extension
        if not filename.endswith('.json'):
            filename += '.json'
            
        filepath = os.path.join(self.json_dir, filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"Data saved to {filepath}")
            return filepath
        except Exception as e:
            print(f"Error saving JSON: {str(e)}")
            return None
    
    def load_from_json(self, filename):
        """
        Load data from JSON file
        
        Args:
            filename: Name of the JSON file to load
            
        Returns:
            List of dictionaries or None if error
        """
        if not filename.endswith('.json'):
            filename += '.json'
            
        filepath = os.path.join(self.json_dir, filename)
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            print(f"Data loaded from {filepath}")
            return data
        except FileNotFoundError:
            print(f"File not found: {filepath}")
            return None
        except Exception as e:
            print(f"Error loading JSON: {str(e)}")
            return None
    
    def load_from_csv(self, filename):
        """
        Load data from CSV file
        
        Args:
            filename: Name of the CSV file to load
            
        Returns:
            DataFrame or None if error
        """
        if not filename.endswith('.csv'):
            filename += '.csv'
            
        filepath = os.path.join(self.csv_dir, filename)
        
        try:
            df = pd.read_csv(filepath, encoding='utf-8')
            print(f"Data loaded from {filepath}")
            return df
        except FileNotFoundError:
            print(f"File not found: {filepath}")
            return None
        except Exception as e:
            print(f"Error loading CSV: {str(e)}")
            return None
    
    def list_files(self, file_type="both"):
        """
        List available files in output directories
        
        Args:
            file_type: "json", "csv", or "both"
            
        Returns:
            Dictionary with file lists
        """
        files = {"json": [], "csv": []}
        
        if file_type in ["json", "both"]:
            try:
                files["json"] = [f for f in os.listdir(self.json_dir) if f.endswith('.json')]
            except FileNotFoundError:
                files["json"] = []
        
        if file_type in ["csv", "both"]:
            try:
                files["csv"] = [f for f in os.listdir(self.csv_dir) if f.endswith('.csv')]
            except FileNotFoundError:
                files["csv"] = []
        
        return files
    
    def save_detailed_products(self, products_with_details, timestamp=None):
        """
        Save products with detailed information in both formats
        
        Args:
            products_with_details: List of products with details
            timestamp: Optional timestamp string, if None uses current time
            
        Returns:
            Dictionary with paths of saved files
        """
        if timestamp is None:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
        
        json_filename = f"tokopedia_products_with_details_{timestamp}.json"
        csv_filename = f"tokopedia_products_flat_{timestamp}.csv"
        
        json_path = self.save_to_json(products_with_details, json_filename)
        csv_path = self.save_to_csv(products_with_details, csv_filename)
        
        return {
            "json": json_path,
            "csv": csv_path,
            "timestamp": timestamp
        }
    
    def get_file_info(self, filename, file_type="json"):
        """
        Get information about a file
        
        Args:
            filename: Name of the file
            file_type: "json" or "csv"
            
        Returns:
            Dictionary with file information
        """
        if file_type == "json":
            filepath = os.path.join(self.json_dir, filename)
        else:
            filepath = os.path.join(self.csv_dir, filename)
        
        try:
            stat = os.stat(filepath)
            return {
                "filename": filename,
                "filepath": filepath,
                "size_bytes": stat.st_size,
                "size_mb": round(stat.st_size / (1024 * 1024), 2),
                "created": time.ctime(stat.st_ctime),
                "modified": time.ctime(stat.st_mtime)
            }
        except FileNotFoundError:
            return None
        except Exception as e:
            print(f"Error getting file info: {str(e)}")
            return None
    
    def cleanup_old_files(self, days_old=7, file_type="both"):
        """
        Remove files older than specified days
        
        Args:
            days_old: Number of days (files older than this will be removed)
            file_type: "json", "csv", or "both"
            
        Returns:
            List of removed files
        """
        import time as time_module
        
        cutoff_time = time_module.time() - (days_old * 24 * 60 * 60)
        removed_files = []
        
        directories = []
        if file_type in ["json", "both"]:
            directories.append((self.json_dir, ".json"))
        if file_type in ["csv", "both"]:
            directories.append((self.csv_dir, ".csv"))
        
        for directory, extension in directories:
            try:
                for filename in os.listdir(directory):
                    if filename.endswith(extension):
                        filepath = os.path.join(directory, filename)
                        if os.path.getctime(filepath) < cutoff_time:
                            os.remove(filepath)
                            removed_files.append(filepath)
                            print(f"Removed old file: {filepath}")
            except FileNotFoundError:
                continue
            except Exception as e:
                print(f"Error during cleanup: {str(e)}")
        
        return removed_files