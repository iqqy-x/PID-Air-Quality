"""
Main pipeline orchestrator for the air quality monitoring system.
"""

import sys
from typing import List, Callable

from src.ingest.weather_ingest import run_ingest
from src.database.insert_data import insert_raw_data
from src.transform.clean_transform import clean_transform
from src.transform.daily_batch import run_daily_batch
from src.analysis.city_ispa_joined import build_city_ispa
from src.utils.logger import get_logger

logger = get_logger(__name__)


class PipelineStep:
    """Represents a step in the data pipeline."""
    
    def __init__(self, name: str, func: Callable, description: str):
        """Initialize a pipeline step.
        
        Args:
            name: Step identifier
            func: Callable to execute
            description: Human-readable description
        """
        self.name = name
        self.func = func
        self.description = description
    
    def execute(self) -> bool:
        """Execute the pipeline step.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info(f"\n[STEP: {self.name}] {self.description}")
            logger.info("-" * 60)
            self.func()
            logger.info(f"✓ {self.name} completed successfully\n")
            return True
        except Exception as e:
            logger.error(f"✗ {self.name} failed: {e}\n")
            return False


class DataPipeline:
    """Orchestrates the complete data pipeline."""
    
    def __init__(self):
        """Initialize the pipeline with all steps."""
        self.steps = [
            PipelineStep(
                name="INGEST",
                func=run_ingest,
                description="Ingesting data from WeatherAPI (weather + air quality)"
            ),
            PipelineStep(
                name="INSERT",
                func=insert_raw_data,
                description="Inserting raw JSON data into PostgreSQL"
            ),
            PipelineStep(
                name="TRANSFORM",
                func=clean_transform,
                description="Cleaning and transforming raw data"
            ),
            PipelineStep(
                name="AGGREGATE",
                func=run_daily_batch,
                description="Aggregating daily metrics per city"
            ),
            PipelineStep(
                name="ANALYZE",
                func=build_city_ispa,
                description="Building city-level ISPA join"
            ),
        ]
        self.successful_steps = 0
        self.failed_steps = 0
    
    def run(self) -> bool:
        """Run the complete pipeline.
        
        Returns:
            True if all steps succeeded, False otherwise
        """
        logger.info("\n" + "=" * 60)
        logger.info("AIR QUALITY MONITORING PIPELINE")
        logger.info("=" * 60)
        logger.info(f"Total steps: {len(self.steps)}\n")
        
        for i, step in enumerate(self.steps, 1):
            logger.info(f"[{i}/{len(self.steps)}] Starting {step.name}...")
            
            if step.execute():
                self.successful_steps += 1
            else:
                self.failed_steps += 1
                logger.warning(f"Continuing with next step...\n")
        
        # Summary
        logger.info("=" * 60)
        logger.info("PIPELINE EXECUTION SUMMARY")
        logger.info("=" * 60)
        logger.info(f"✓ Successful steps: {self.successful_steps}/{len(self.steps)}")
        logger.info(f"✗ Failed steps: {self.failed_steps}/{len(self.steps)}")
        
        if self.failed_steps == 0:
            logger.info("\n✓ All pipeline steps completed successfully!")
        else:
            logger.warning(f"\n⚠ {self.failed_steps} step(s) failed. Check logs above.")
        
        logger.info("=" * 60 + "\n")
        
        return self.failed_steps == 0


def run_pipeline() -> int:
    """Run the complete ETL pipeline.
    
    Returns:
        Exit code (0 if successful, 1 if failed)
    """
    try:
        pipeline = DataPipeline()
        success = pipeline.run()
        return 0 if success else 1
    except Exception as e:
        logger.error(f"Pipeline crashed: {e}")
        return 1


if __name__ == "__main__":
    exit_code = run_pipeline()
    sys.exit(exit_code)
