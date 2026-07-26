from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = (
    ROOT / ".github" / "workflows" / "content-radar-daily.yml"
)


class WorkflowContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.workflow = WORKFLOW.read_text(encoding="utf-8")

    def test_has_all_schedules_dispatch_modes_and_schedule_mapping(self) -> None:
        for cron in (
            "30 16 * * *",
            "0 20 * * *",
            "30 22 * * *",
            "20 23 * * *",
        ):
            self.assertIn(cron, self.workflow)
            self.assertIn(f'"{cron}"', self.workflow)
        for mode in (
            "snapshot",
            "build",
            "fixture-small",
            "fixture-maximum",
        ):
            self.assertIn(f"- {mode}", self.workflow)
        self.assertIn("github.event.schedule", self.workflow)
        self.assertIn('schedule == "30 16 * * *"', self.workflow)
        self.assertIn('schedule == "0 20 * * *"', self.workflow)
        self.assertIn('schedule in {"30 22 * * *", "20 23 * * *"}', self.workflow)
        self.assertIn('ZoneInfo("Asia/Shanghai")', self.workflow)

    def test_all_dependencies_are_immutable(self) -> None:
        for sha in (
            "fbc6f3992d24b796d5a048ff273f7fcc4a7b6c09",
            "ece7cb06caefa5fff74198d8649806c4678c61a1",
            "ea165f8d65b6e75b540449e92b4886f43607fa02",
            "983d7736d9b0ae728b81ab479565c72886d7745b",
            "7b1f4a764d45c48632c6b24a0339c27f5614fb0b",
            "d6db90164ac5ed86f2b6aed7e0febac5b3c0c03e",
            "fb89342bf775608dee05a24586ddbac47c86a606",
        ):
            self.assertIn(sha, self.workflow)
        self.assertNotRegex(self.workflow, r"uses:\s+[^\s]+@v\d")

    def test_jobs_permissions_and_concurrency_are_scoped(self) -> None:
        for job in ("metadata:", "collection:", "build:", "publish:"):
            self.assertIn(job, self.workflow)
        self.assertIn("permissions: {}", self.workflow)
        self.assertIn("contents: read", self.workflow)
        self.assertIn("actions: read", self.workflow)
        self.assertIn("pages: write", self.workflow)
        self.assertIn("id-token: write", self.workflow)
        self.assertIn(
            "publish:\n"
            "    needs: build\n"
            "    if: >-\n"
            "      always() &&\n"
            "      needs.build.result == 'success'",
            self.workflow,
        )
        self.assertIn("group: content-radar-pages", self.workflow)
        self.assertIn("cancel-in-progress: false", self.workflow)
        self.assertNotIn("pull_request_target", self.workflow)
        self.assertNotIn("secrets.", self.workflow)

    def test_collection_artifact_and_build_publish_order_are_explicit(self) -> None:
        self.assertIn("trendradar-snapshot-${{ needs.metadata.outputs.report_date }}-${{ needs.metadata.outputs.logical_slot }}", self.workflow)
        self.assertIn("retention-days: 4", self.workflow)
        self.assertIn("needs.metadata.outputs.collect == 'true'", self.workflow)
        self.assertIn("needs.metadata.outputs.build == 'true'", self.workflow)
        self.assertIn("download_latest_snapshots", self.workflow)
        self.assertIn("python -m unittest discover", self.workflow)
        self.assertIn("PYTHONDONTWRITEBYTECODE: \"1\"", self.workflow)
        self.assertIn("python -m content_radar_feed.cli build-report", self.workflow)
        self.assertIn("python -m content_radar_feed.cli build-fixture", self.workflow)
        validate = self.workflow.index(
            "python -m content_radar_feed.cli validate-report"
        )
        upload = self.workflow.index(
            "actions/upload-pages-artifact@"
        )
        deploy = self.workflow.index("actions/deploy-pages@")
        self.assertLess(validate, upload)
        self.assertLess(upload, deploy)
        self.assertRegex(
            self.workflow,
            re.compile(r"sha256sum .*reports/.*\.json", re.MULTILINE),
        )

    def test_validated_real_report_is_committed_to_feed_branch(self) -> None:
        self.assertIn("contents: write", self.workflow)
        self.assertIn("Publish verified raw report", self.workflow)
        self.assertIn("git fetch --depth=1 origin feed", self.workflow)
        self.assertIn(
            'git -C "$feed_dir" push origin HEAD:feed',
            self.workflow,
        )
        self.assertIn(
            "needs.metadata.outputs.mode == 'scheduled' || "
            "needs.metadata.outputs.mode == 'build'",
            self.workflow,
        )
        validate = self.workflow.index(
            "Validate report before Pages packaging"
        )
        raw_publish = self.workflow.index("Publish verified raw report")
        self.assertLess(validate, raw_publish)


if __name__ == "__main__":
    unittest.main()
