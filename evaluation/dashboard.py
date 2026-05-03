# evaluation/dashboard.py

import os
import glob
from evaluation.metrics import EvaluationFramework

def run_all_evaluations():
    """
    Run evaluation on all 8 challenge outputs.
    Generates complete evaluation report.
    """
    
    evaluator = EvaluationFramework()
    
    print("\n" + "="*60)
    print("ARA-1 EVALUATION FRAMEWORK")
    print("Running 22 metrics across 8 challenges")
    print("="*60 + "\n")
    
    # Find all challenge files
    challenge_files = sorted(glob.glob("results/challenge_*.md"))
    
    if not challenge_files:
        print("No challenge files found in results/")
        print("Run the agent on challenges first")
        return
    
    print(f"Found {len(challenge_files)} challenge files\n")
    
    # Evaluate each challenge
    for filepath in challenge_files:
        challenge_id = os.path.basename(filepath).replace('.md', '')
        
        # Skip non-challenge files
        if not any(f"challenge_{i}" in challenge_id 
                   for i in range(1, 9)):
            continue
        
        print(f"\nEvaluating {challenge_id}...")
        
        try:
            with open(filepath, 'r') as f:
                report_content = f.read()
            
            if len(report_content.split()) < 50:
                print(f"  Skipping — report too short")
                continue
            
            result = evaluator.evaluate_report(
                report=report_content,
                challenge_id=challenge_id
            )
            
            print(f"  Score: {result['overall_score']}/100")
            
        except Exception as e:
            print(f"  Error evaluating {challenge_id}: {e}")
    
    # Save complete report
    evaluator.save_results()
    
    # Print summary
    if evaluator.results:
        print("\n" + "="*60)
        print("EVALUATION COMPLETE")
        print("="*60)
        
        scores = [
            r["overall_score"] 
            for r in evaluator.results.values()
        ]
        
        print(f"\nChallenges evaluated: {len(scores)}")
        print(f"Average score: {sum(scores)/len(scores):.1f}/100")
        print(f"Highest score: {max(scores):.1f}/100")
        print(f"Lowest score: {min(scores):.1f}/100")
        print(f"Challenges passing (≥70): {sum(1 for s in scores if s >= 70)}/{len(scores)}")
        print(f"\nReport saved to: results/evaluation_report.md")
    
    return evaluator


if __name__ == "__main__":
    run_all_evaluations()