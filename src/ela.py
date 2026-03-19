#!/usr/bin/env python3
"""
Error Level Analysis (ELA) Module

Analyzes JPEG compression artifacts to detect manipulation.
"""

import os
import numpy as np
from PIL import Image, ImageChops
from pathlib import Path
import matplotlib.pyplot as plt
import json

def perform_ela(image_path, quality=90):
    """
    Perform Error Level Analysis on an image.

    Args:
        image_path (str): Path to the original image
        quality (int): JPEG quality level for re-compression (default: 90)

    Returns:
        dict: ELA analysis results
    """
    try:
        # Open original image
        original = Image.open(image_path)

        # Ensure RGB mode
        if original.mode != 'RGB':
            original = original.convert('RGB')

        # Save original as JPEG with specified quality
        temp_path = f"./results/temp_ela_{Path(image_path).stem}.jpg"
        original.save(temp_path, 'JPEG', quality=quality)

        # Open the re-saved image
        recompressed = Image.open(temp_path)

        # Calculate difference
        ela_image = ImageChops.difference(original, recompressed)

        # Convert to numpy array for analysis
        ela_array = np.array(ela_image)

        # Calculate ELA statistics
        ela_mean = np.mean(ela_array)
        ela_std = np.std(ela_array)
        ela_max = np.max(ela_array)
        ela_median = np.median(ela_array)

        # Calculate histogram
        hist, bins = np.histogram(ela_array.flatten(), bins=256, range=(0, 255))

        # Find the peak of the histogram (most common error level)
        peak_error_level = np.argmax(hist)

        # Calculate entropy of error distribution
        hist_normalized = hist / np.sum(hist)
        entropy = -np.sum(hist_normalized * np.log2(hist_normalized + 1e-10))

        # Assess manipulation likelihood
        if ela_std < 5:
            manipulation_likelihood = "Very low - homogeneous compression"
            score = 0.1
        elif ela_std < 10:
            manipulation_likelihood = "Low - consistent compression"
            score = 0.2
        elif ela_std < 20:
            manipulation_likelihood = "Moderate - some compression variations"
            score = 0.4
        elif ela_std < 30:
            manipulation_likelihood = "High - significant compression artifacts"
            score = 0.7
        else:
            manipulation_likelihood = "Very high - heavy manipulation likely"
            score = 0.9

        # Clean up temp file
        if os.path.exists(temp_path):
            os.remove(temp_path)

        return {
            "ela_score": round(ela_std, 2),
            "ela_mean": round(ela_mean, 2),
            "ela_median": round(ela_median, 2),
            "ela_max": round(ela_max, 2),
            "peak_error_level": int(peak_error_level),
            "entropy": round(entropy, 3),
            "manipulation_likelihood": manipulation_likelihood,
            "manipulation_score": score
        }

    except Exception as e:
        # Clean up temp file if it exists
        temp_path = f"./results/temp_ela_{Path(image_path).stem}.jpg"
        if os.path.exists(temp_path):
            os.remove(temp_path)
        return {"error": f"ELA analysis failed: {str(e)}"}

def create_ela_visualization(image_path, output_path, quality=90):
    """
    Create ELA visualization image.

    Args:
        image_path (str): Path to original image
        output_path (str): Path to save ELA visualization
        quality (int): JPEG quality for re-compression
    """
    try:
        # Open original image
        original = Image.open(image_path)

        if original.mode != 'RGB':
            original = original.convert('RGB')

        # Save and reload with compression
        temp_path = f"./results/temp_ela_vis_{Path(image_path).stem}.jpg"
        original.save(temp_path, 'JPEG', quality=quality)
        recompressed = Image.open(temp_path)

        # Create ELA image
        ela_image = ImageChops.difference(original, recompressed)

        # Enhance visibility (multiply by factor)
        ela_array = np.array(ela_image) * 10
        ela_array = np.clip(ela_array, 0, 255).astype(np.uint8)
        ela_enhanced = Image.fromarray(ela_array)

        # Save visualization
        ela_enhanced.save(output_path)

        # Clean up
        if os.path.exists(temp_path):
            os.remove(temp_path)

        return True

    except Exception as e:
        # Clean up
        temp_path = f"./results/temp_ela_vis_{Path(image_path).stem}.jpg"
        if os.path.exists(temp_path):
            os.remove(temp_path)
        return False

def analyze_ela_batch(input_dir="./processed", output_dir="./results/ela"):
    """
    Perform ELA analysis on all images in a directory.

    Args:
        input_dir (str): Directory containing images
        output_dir (str): Directory to save ELA visualizations

    Returns:
        dict: ELA results for all images
    """
    results = {}
    os.makedirs(output_dir, exist_ok=True)

    for file_path in Path(input_dir).iterdir():
        if file_path.suffix.lower() in {'.jpg', '.jpeg', '.png'}:
            print(f"Performing ELA analysis: {file_path.name}")

            # Perform ELA analysis
            ela_result = perform_ela(str(file_path))

            # Create visualization
            vis_path = os.path.join(output_dir, f"ela_{file_path.stem}.jpg")
            vis_success = create_ela_visualization(str(file_path), vis_path)

            ela_result["visualization_created"] = vis_success
            ela_result["visualization_path"] = vis_path

            results[file_path.name] = ela_result

    return results

def main():
    """Main ELA analysis function."""
    ela_results = analyze_ela_batch()

    # Save results
    output_file = "./results/ela_analysis.json"
    with open(output_file, "w") as f:
        json.dump(ela_results, f, indent=2)

    print("ELA analysis complete!")

if __name__ == "__main__":
    main()
