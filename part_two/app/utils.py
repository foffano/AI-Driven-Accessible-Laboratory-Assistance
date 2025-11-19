import csv
import os

def save_results_to_csv(results, csv_path):
    try:
        with open(csv_path, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['Image Name', 'Response', 'Audio Filename'])
            for result in results:
                writer.writerow(result)
        print(f"Results saved to {csv_path}")
    except Exception as e:
        print(f"Error in save_results_to_csv: {e}")