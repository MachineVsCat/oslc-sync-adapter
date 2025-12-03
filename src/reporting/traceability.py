"""Traceability report generation for compliance frameworks."""

import csv
import logging
from io import StringIO
from datetime import datetime

log = logging.getLogger(__name__)


class TraceabilityReport:
    def __init__(self, lqe_reporter):
        self.reporter = lqe_reporter

    def generate_matrix(self, project_area=None, output_format="csv"):
        """Generate a full traceability matrix."""
        matrix = self.reporter.get_traceability_matrix(project_area)
        log.info(f"Generated traceability matrix: {len(matrix)} requirements")

        if output_format == "csv":
            return self._to_csv(matrix)
        return matrix

    def coverage_summary(self):
        """Generate test coverage summary showing gaps."""
        untested = self.reporter.get_untested_requirements()
        return {
            "untested_count": len(untested),
            "requirements": untested,
            "generated_at": datetime.utcnow().isoformat(),
        }

    def _to_csv(self, matrix):
        """Convert matrix to CSV string."""
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow([
            "Requirement", "Title", "Satisfied By",
            "Implemented By", "Validated By"
        ])
        for row in matrix:
            writer.writerow([
                row["requirement"], row["title"],
                row["satisfied_by"], row["implemented_by"],
                row["validated_by"],
            ])
        return output.getvalue()
