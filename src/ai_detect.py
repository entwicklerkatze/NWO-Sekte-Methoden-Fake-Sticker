#!/usr/bin/env python3
"""
AI and Generative Content Detection Module

Detects signs of AI-generated or manipulated content using various heuristics
and pattern analysis.
"""

import os
import numpy as np
from PIL import Image
from pathlib import Path
from skimage import filters, feature
from skimage.color import rgb2gray
import cv2
import json

def detect_symmetry_artifacts(image_path):
    """
    Detect artificial symmetry patterns common in AI-generated images.

    Args:
        image_path (str): Path to image

    Returns:
        dict: Symmetry analysis results
    """
    try:
        img = Image.open(image_path)
        img_array = np.array(img)

        if len(img_array.shape) != 3:
            return {"symmetry_score": 0, "assessment": "Cannot analyze symmetry (grayscale)"}

        # Convert to grayscale
        gray = rgb2gray(img_array)

        # Check vertical symmetry
        left_half = gray[:, :gray.shape[1]//2]
        right_half = np.fliplr(gray[:, gray.shape[1]//2:])

        # Handle odd widths
        min_width = min(left_half.shape[1], right_half.shape[1])
        left_half = left_half[:, :min_width]
        right_half = right_half[:, :min_width]

        vertical_symmetry = np.mean(np.abs(left_half - right_half))

        # Check horizontal symmetry
        top_half = gray[:gray.shape[0]//2, :]
        bottom_half = np.flipud(gray[gray.shape[0]//2:, :])

        min_height = min(top_half.shape[0], bottom_half.shape[0])
        top_half = top_half[:min_height, :]
        bottom_half = bottom_half[:min_height, :]

        horizontal_symmetry = np.mean(np.abs(top_half - bottom_half))

        # Overall symmetry score (lower is more symmetric)
        symmetry_score = (vertical_symmetry + horizontal_symmetry) / 2

        if symmetry_score < 10:
            assessment = "High artificial symmetry detected - potential AI generation"
            confidence = 0.8
        elif symmetry_score < 25:
            assessment = "Moderate symmetry - may be stylized design"
            confidence = 0.4
        else:
            assessment = "Natural asymmetry - likely authentic"
            confidence = 0.1

        return {
            "symmetry_score": round(symmetry_score, 2),
            "vertical_symmetry": round(vertical_symmetry, 2),
            "horizontal_symmetry": round(horizontal_symmetry, 2),
            "assessment": assessment,
            "confidence": confidence
        }

    except Exception as e:
        return {"error": f"Symmetry analysis failed: {str(e)}"}

def detect_edge_consistency(image_path):
    """
    Analyze edge consistency and blending quality.

    Args:
        image_path (str): Path to image

    Returns:
        dict: Edge analysis results
    """
    try:
        img = Image.open(image_path)
        img_array = np.array(img)

        if len(img_array.shape) != 3:
            gray = img_array.astype(float) / 255.0
        else:
            gray = rgb2gray(img_array)

        # Detect edges
        edges = filters.sobel(gray)

        # Calculate edge statistics
        edge_mean = np.mean(edges)
        edge_std = np.std(edges)
        edge_max = np.max(edges)

        # Analyze edge distribution
        hist, bins = np.histogram(edges.flatten(), bins=50, range=(0, 1))
        hist_normalized = hist / np.sum(hist)

        # Look for unnatural edge patterns
        # AI-generated images often have too uniform edge distributions
        entropy = -np.sum(hist_normalized * np.log2(hist_normalized + 1e-10))

        if entropy < 2.0:
            consistency = "Too uniform edges - potential AI generation"
            score = 0.7
        elif entropy < 3.0:
            consistency = "Moderately consistent edges"
            score = 0.4
        else:
            consistency = "Natural edge variation - likely authentic"
            score = 0.1

        return {
            "edge_entropy": round(entropy, 3),
            "edge_mean": round(edge_mean, 3),
            "edge_std": round(edge_std, 3),
            "edge_consistency": consistency,
            "ai_probability": score
        }

    except Exception as e:
        return {"error": f"Edge analysis failed: {str(e)}"}

def detect_texture_artifacts(image_path):
    """
    Detect unnatural texture patterns common in AI generation.

    Args:
        image_path (str): Path to image

    Returns:
        dict: Texture analysis results
    """
    try:
        img = Image.open(image_path)
        img_array = np.array(img)

        if len(img_array.shape) != 3:
            return {"texture_score": 0, "assessment": "Cannot analyze texture (grayscale)"}

        # Convert to grayscale for texture analysis
        gray = rgb2gray(img_array)

        # Calculate GLCM (Gray Level Co-occurrence Matrix) features
        from skimage.feature import graycomatrix, graycoprops

        # Use different offsets for texture analysis
        distances = [1, 2, 3]
        angles = [0, np.pi/4, np.pi/2, 3*np.pi/4]

        glcm_features = {}
        for distance in distances:
            for angle in angles:
                glcm = graycomatrix((gray * 255).astype(np.uint8), distances=[distance],
                                  angles=[angle], levels=256, symmetric=True, normed=True)

                glcm_features[f"contrast_d{distance}_a{int(np.degrees(angle))}"] = graycoprops(glcm, 'contrast')[0, 0]
                glcm_features[f"homogeneity_d{distance}_a{int(np.degrees(angle))}"] = graycoprops(glcm, 'homogeneity')[0, 0]

        # Calculate texture uniformity score
        contrasts = [v for k, v in glcm_features.items() if 'contrast' in k]
        homogeneities = [v for k, v in glcm_features.items() if 'homogeneity' in k]

        avg_contrast = np.mean(contrasts)
        avg_homogeneity = np.mean(homogeneities)

        # AI-generated textures often have too uniform patterns
        texture_uniformity = avg_homogeneity / (avg_contrast + 1)

        if texture_uniformity > 0.8:
            assessment = "Extremely uniform texture - potential AI generation"
            score = 0.9
        elif texture_uniformity > 0.6:
            assessment = "Very uniform texture - may be AI-generated"
            score = 0.7
        elif texture_uniformity > 0.4:
            assessment = "Moderately uniform texture"
            score = 0.4
        else:
            assessment = "Natural texture variation - likely authentic"
            score = 0.1

        return {
            "texture_uniformity": round(texture_uniformity, 3),
            "average_contrast": round(avg_contrast, 3),
            "average_homogeneity": round(avg_homogeneity, 3),
            "assessment": assessment,
            "ai_probability": score
        }

    except Exception as e:
        return {"error": f"Texture analysis failed: {str(e)}"}

def detect_ai_artifacts(image_path):
    """
    Comprehensive AI detection analysis.

    Args:
        image_path (str): Path to image

    Returns:
        dict: Complete AI detection results
    """
    symmetry = detect_symmetry_artifacts(image_path)
    edges = detect_edge_consistency(image_path)
    texture = detect_texture_artifacts(image_path)

    # Combine probabilities
    probabilities = []
    if "confidence" in symmetry:
        probabilities.append(symmetry["confidence"])
    if "ai_probability" in edges:
        probabilities.append(edges["ai_probability"])
    if "ai_probability" in texture:
        probabilities.append(texture["ai_probability"])

    if probabilities:
        overall_ai_probability = np.mean(probabilities)

        if overall_ai_probability > 0.7:
            verdict = "High probability of AI generation"
            confidence = 0.85
        elif overall_ai_probability > 0.5:
            verdict = "Moderate AI indicators present"
            confidence = 0.6
        elif overall_ai_probability > 0.3:
            verdict = "Some AI-like characteristics"
            confidence = 0.4
        else:
            verdict = "Low AI probability - likely authentic"
            confidence = 0.2
    else:
        overall_ai_probability = 0
        verdict = "Analysis incomplete"
        confidence = 0

    return {
        "symmetry_analysis": symmetry,
        "edge_analysis": edges,
        "texture_analysis": texture,
        "overall_ai_probability": round(overall_ai_probability, 3),
        "verdict": verdict,
        "confidence": confidence
    }

def main():
    """Detect AI artifacts in all processed stickers."""
    input_dir = "./processed"
    output_file = "./results/ai_detection_analysis.json"

    results = {}

    # Analyze all sticker images
    for file_path in Path(input_dir).iterdir():
        if file_path.suffix.lower() in {'.jpg', '.jpeg', '.png'}:
            print(f"Analyzing AI detection: {file_path.name}")
            results[file_path.name] = detect_ai_artifacts(str(file_path))

    # Save results
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)

    print("AI detection analysis complete!")

if __name__ == "__main__":
    main()
