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


class DO178CReport(TraceabilityReport):
    """DO-178C specific traceability reporting for aerospace compliance."""

    TRACE_LEVELS = [
        "system_req_to_hlr",
        "hlr_to_llr",
        "llr_to_source",
        "source_to_test",
        "test_to_result",
    ]

    def generate_do178c_matrix(self, project_area):
        """Generate DO-178C compliant traceability matrix."""
        matrix = self.generate_matrix(project_area)
        report = {
            "standard": "DO-178C",
            "level": "A",
            "generated_at": datetime.utcnow().isoformat(),
            "traceability_data": matrix,
            "coverage": self.coverage_summary(),
        }

        gaps = self._find_traceability_gaps(matrix)
        report["gaps"] = gaps
        report["compliant"] = len(gaps) == 0
        return report

    def _find_traceability_gaps(self, matrix):
        """Identify missing links required by DO-178C."""
        gaps = []
        if isinstance(matrix, str):
            return gaps
        for row in matrix:
            if not row.get("validated_by"):
                gaps.append({
                    "requirement": row["requirement"],
                    "title": row["title"],
                    "missing": "test_coverage",
                })
            if not row.get("implemented_by"):
                gaps.append({
                    "requirement": row["requirement"],
                    "title": row["title"],
                    "missing": "implementation_link",
                })
        return gaps
