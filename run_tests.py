#!/usr/bin/env python
"""Simple wrapper to run agent evaluation with proper encoding."""

import sys
import os

# Fix Windows console encoding
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except:
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Import and run the evaluation
from evaluate_agents import evaluate_agents
import asyncio

if __name__ == "__main__":
    print("\n" + "="*60)
    print("  AGENT ACCURACY EVALUATION")
    print("="*60 + "\n")
    
    try:
        metrics = asyncio.run(evaluate_agents())
        print("\nEvaluation completed successfully!")
        print("\nResults saved in: evaluation_results/")
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)
