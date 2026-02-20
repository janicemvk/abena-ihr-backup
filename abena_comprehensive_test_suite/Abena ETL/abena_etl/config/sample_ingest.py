from abena_etl import TransformationEngine
from pathlib import Path

if __name__ == "__main__":
    # Define robust, cross-platform paths
    project_root = Path(__file__).resolve().parent.parent
    source_path = project_root / "data" / "custom_emr_export.csv"
    output_dir = project_root / "data" / "fhir_output"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "custom_emr_transformed"

    engine = TransformationEngine()
    try:
        # Example: process a batch file from a custom EMR
        result = engine.process_batch(
            source_path=str(source_path),
            source_system="CustomEMR",
            output_path=str(output_path)
        )
        print("Batch Ingestion Result:")
        print(result)
    finally:
        engine.stop() 