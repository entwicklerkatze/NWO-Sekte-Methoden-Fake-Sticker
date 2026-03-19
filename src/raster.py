#!/usr/bin/env python3
"""
Raster and Print Quality Analysis Module

Analyzes print quality, DPI estimation, and printing method detection.
"""

import os
import numpy as np
from PIL import Image
from pathlib import Path
from skimage import filters, transform
from skimage.color import rgb2gray
import cv2
import json

def estimate_dpi(image_path):
    """
    Estimate DPI from image characteristics and pixel density.

    Args:
        image_path (str): Path to image

    Returns:
        dict: DPI estimation results
    """
    try:
        img = Image.open(image_path)

        # Get image dimensions in pixels
        width_px, height_px = img.size

        # Estimate physical size (assuming typical sticker sizes)
        # Most collectible stickers are 2-5 cm, assume average 3.5 cm
        assumed_physical_size_cm = 3.5

        # Convert to inches (1 inch = 2.54 cm)
        assumed_physical_size_inches = assumed_physical_size_cm / 2.54

        # Calculate estimated DPI
        dpi_width = width_px / assumed_physical_size_inches
        dpi_height = height_px / assumed_physical_size_inches
        estimated_dpi = (dpi_width + dpi_height) / 2

        # Classify DPI range
        if estimated_dpi < 150:
            quality = "Low resolution - possible digital print or scan"
            confidence = 0.6
        elif estimated_dpi < 300:
            quality = "Medium resolution - typical inkjet print"
            confidence = 0.7
        elif estimated_dpi < 600:
            quality = "High resolution - professional offset print"
            confidence = 0.8
        else:
            quality = "Very high resolution - likely digital source"
            confidence = 0.5

        return {
            "estimated_dpi": round(estimated_dpi, 1),
            "dpi_width": round(dpi_width, 1),
            "dpi_height": round(dpi_height, 1),
            "assumed_physical_size_cm": assumed_physical_size_cm,
            "quality_assessment": quality,
            "confidence": confidence
        }

    except Exception as e:
        return {"error": f"DPI estimation failed: {str(e)}"}

def analyze_raster_pattern(image_path):
    """
    Analyze raster dot patterns to determine printing method.

    Args:
        image_path (str): Path to image

    Returns:
        dict: Raster analysis results
    """
    try:
        img = Image.open(image_path)

        # Convert to grayscale for analysis
        if img.mode == 'RGB':
            gray = np.array(img.convert('L'))
        else:
            gray = np.array(img)

        # Look for periodic patterns using FFT
        fft = np.fft.fft2(gray)
        fft_shift = np.fft.fftshift(fft)
        magnitude_spectrum = np.abs(fft_shift)

        # Analyze frequency domain
        # Look for peaks that might indicate screen frequencies
        center_y, center_x = magnitude_spectrum.shape[0] // 2, magnitude_spectrum.shape[1] // 2

        # Remove DC component
        magnitude_spectrum[center_y-5:center_y+5, center_x-5:center_x+5] = 0

        # Find frequency peaks
        peaks = []
        threshold = np.percentile(magnitude_spectrum, 95)  # Top 5% as peaks

        for i in range(1, magnitude_spectrum.shape[0]-1):
            for j in range(1, magnitude_spectrum.shape[1]-1):
                if magnitude_spectrum[i,j] > threshold:
                    # Calculate frequency from distance from center
                    freq_y = abs(i - center_y) / magnitude_spectrum.shape[0]
                    freq_x = abs(j - center_x) / magnitude_spectrum.shape[1]
                    frequency = np.sqrt(freq_y**2 + freq_x**2)
                    peaks.append(frequency)

        # Analyze peak frequencies
        if peaks:
            avg_peak_freq = np.mean(peaks)
            max_peak_freq = np.max(peaks)

            # Common screen frequencies (lines per inch)
            # Offset printing: 133-200 lpi
            # Flexo: 85-133 lpi
            # Digital/Inkjet: varies, often lower
            if max_peak_freq > 0.3:  # High frequency patterns
                raster_type = "Offset printing (high screen frequency)"
                confidence = 0.8
            elif max_peak_freq > 0.2:
                raster_type = "Professional flexographic printing"
                confidence = 0.7
            elif max_peak_freq > 0.1:
                raster_type = "Digital printing or lower quality offset"
                confidence = 0.6
            else:
                raster_type = "No clear raster pattern detected"
                confidence = 0.3
        else:
            raster_type = "No significant periodic patterns found"
            confidence = 0.4

        return {
            "raster_type": raster_type,
            "confidence": confidence,
            "average_peak_frequency": round(avg_peak_freq, 4) if peaks else 0,
            "max_peak_frequency": round(max_peak_freq, 4) if peaks else 0,
            "num_peaks_detected": len(peaks)
        }

    except Exception as e:
        return {"error": f"Raster analysis failed: {str(e)}"}

def detect_moire_patterns(image_path):
    """
    Detect moiré patterns that might indicate scanning or resampling.

    Args:
        image_path (str): Path to image

    Returns:
        dict: Moire detection results
    """
    try:
        img = Image.open(image_path)
        gray = np.array(img.convert('L')) if img.mode == 'RGB' else np.array(img)

        # Apply high-pass filter to enhance interference patterns
        kernel = np.array([[-1,-1,-1],
                          [-1, 8,-1],
                          [-1,-1,-1]])
        high_pass = cv2.filter2D(gray, -1, kernel)

        # Look for periodic interference patterns
        fft = np.fft.fft2(high_pass)
        magnitude = np.abs(np.fft.fftshift(fft))

        # Analyze frequency content for moiré indicators
        center = magnitude.shape[0] // 2
        quarter_region = magnitude[center//2:3*center//2, center//2:3*center//2]

        # Calculate variance in frequency domain
        freq_variance = np.var(quarter_region)

        # Moire often shows as high variance in specific frequency ranges
        if freq_variance > np.percentile(magnitude, 90):
            moire_detected = True
            severity = "Significant moiré patterns detected"
            score = 0.8
        elif freq_variance > np.percentile(magnitude, 75):
            moire_detected = True
            severity = "Moderate moiré patterns"
            score = 0.6
        else:
            moire_detected = False
            severity = "No significant moiré patterns"
            score = 0.1

        return {
            "moire_detected": moire_detected,
            "severity": severity,
            "score": score,
            "frequency_variance": round(freq_variance, 2)
        }

    except Exception as e:
        return {"error": f"Moire detection failed: {str(e)}"}

def analyze_color_registration(image_path):
    """
    Analyze color registration quality.

    Args:
        image_path (str): Path to image

    Returns:
        dict: Color registration analysis
    """
    try:
        img = Image.open(image_path)

        if img.mode != 'RGB':
            return {"registration_quality": "Cannot analyze (not RGB)"}

        rgb = np.array(img)

        # Split into channels
        r, g, b = rgb[:,:,0], rgb[:,:,1], rgb[:,:,2]

        # Calculate channel differences
        rg_diff = np.abs(r.astype(float) - g.astype(float))
        rb_diff = np.abs(r.astype(float) - b.astype(float))
        gb_diff = np.abs(g.astype(float) - b.astype(float))

        # Calculate registration metrics
        avg_rg_diff = np.mean(rg_diff)
        avg_rb_diff = np.mean(rb_diff)
        avg_gb_diff = np.mean(gb_diff)

        max_channel_diff = max(avg_rg_diff, avg_rb_diff, avg_gb_diff)

        # Assess registration quality
        if max_channel_diff < 2:
            quality = "Excellent color registration"
            score = 0.9
        elif max_channel_diff < 5:
            quality = "Good color registration"
            score = 0.7
        elif max_channel_diff < 10:
            quality = "Moderate color registration"
            score = 0.5
        elif max_channel_diff < 20:
            quality = "Poor color registration - possible digital print"
            score = 0.3
        else:
            quality = "Very poor registration - likely low-quality print"
            score = 0.1

        return {
            "registration_quality": quality,
            "score": score,
            "max_channel_difference": round(max_channel_diff, 2),
            "avg_rg_difference": round(avg_rg_diff, 2),
            "avg_rb_difference": round(avg_rb_diff, 2),
            "avg_gb_difference": round(avg_gb_diff, 2)
        }

    except Exception as e:
        return {"error": f"Color registration analysis failed: {str(e)}"}

def analyze_print_quality(image_path):
    """
    Comprehensive print quality analysis.

    Args:
        image_path (str): Path to image

    Returns:
        dict: Complete print quality analysis
    """
    dpi_analysis = estimate_dpi(image_path)
    raster_analysis = analyze_raster_pattern(image_path)
    moire_analysis = detect_moire_patterns(image_path)
    registration_analysis = analyze_color_registration(image_path)

    # Combine analyses for overall assessment
    scores = []
    if "confidence" in dpi_analysis:
        scores.append(dpi_analysis["confidence"])
    if "confidence" in raster_analysis:
        scores.append(raster_analysis["confidence"])
    if "score" in registration_analysis:
        scores.append(registration_analysis["score"])

    if scores:
        overall_quality = np.mean(scores)

        if overall_quality > 0.7:
            verdict = "High-quality professional printing"
        elif overall_quality > 0.5:
            verdict = "Moderate quality printing"
        else:
            verdict = "Low-quality printing or digital reproduction"
    else:
        overall_quality = 0
        verdict = "Analysis incomplete"

    return {
        "dpi_analysis": dpi_analysis,
        "raster_analysis": raster_analysis,
        "moire_analysis": moire_analysis,
        "color_registration": registration_analysis,
        "overall_quality_score": round(overall_quality, 3),
        "print_verdict": verdict
    }

def main():
    """Analyze print quality for all processed stickers."""
    input_dir = "./processed"
    output_file = "./results/print_quality_analysis.json"

    results = {}

    for file_path in Path(input_dir).iterdir():
        if file_path.suffix.lower() in {'.jpg', '.jpeg', '.png'}:
            print(f"Analyzing print quality: {file_path.name}")
            results[file_path.name] = analyze_print_quality(str(file_path))

    # Save results
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)

    print("Print quality analysis complete!")

if __name__ == "__main__":
    main()
