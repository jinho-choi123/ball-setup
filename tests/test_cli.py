from ball_setup.cli import parse_args


class TestParseArgs:
    def test_default(self):
        args = parse_args([])
        assert args.all is False
        assert args.only is None
        assert args.dry_run is False

    def test_all_flag(self):
        args = parse_args(["--all"])
        assert args.all is True

    def test_only_flag(self):
        args = parse_args(["--only", "dev,runtime"])
        assert args.only == "dev,runtime"

    def test_dry_run(self):
        args = parse_args(["--dry-run"])
        assert args.dry_run is True

    def test_combined(self):
        args = parse_args(["--all", "--dry-run"])
        assert args.all is True
        assert args.dry_run is True
