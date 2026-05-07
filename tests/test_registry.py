from ball_setup.registry import Tool, CATEGORIES, TOOLS


class TestTool:
    def test_tool_creation(self):
        tool = Tool(
            name="test-tool",
            category="dev",
            check_cmd="test-cmd",
            pkg={"ubuntu": "test-pkg"},
        )
        assert tool.name == "test-tool"
        assert tool.category == "dev"
        assert tool.check_cmd == "test-cmd"
        assert tool.pkg == {"ubuntu": "test-pkg"}

    def test_tool_list_check_cmd(self):
        tool = Tool(name="fd", category="dev", check_cmd=["fd", "fdfind"])
        assert isinstance(tool.check_cmd, list)


class TestCategories:
    def test_essential_locked(self):
        assert CATEGORIES["essential"]["locked"] is True

    def test_shell_locked(self):
        assert CATEGORIES["shell"]["locked"] is True

    def test_dev_unlocked(self):
        assert CATEGORIES["dev"]["locked"] is False

    def test_all_categories_have_label(self):
        for cat_id, cat in CATEGORIES.items():
            assert "label" in cat, f"Category '{cat_id}' missing label"


class TestToolsRegistry:
    def test_no_duplicate_names(self):
        names = [t.name for t in TOOLS]
        assert len(names) == len(set(names)), f"Duplicates: {[n for n in names if names.count(n) > 1]}"

    def test_all_tools_have_valid_category(self):
        for tool in TOOLS:
            assert tool.category in CATEGORIES, f"{tool.name} has invalid category '{tool.category}'"

    def test_tools_with_check_cmd_have_valid_type(self):
        for tool in TOOLS:
            if tool.check_cmd is not None:
                assert isinstance(tool.check_cmd, (str, list)), f"{tool.name} has invalid check_cmd type"

    def test_tools_without_check_cmd_have_custom_installer(self):
        for tool in TOOLS:
            if tool.check_cmd is None:
                assert tool.custom_installer is not None, f"{tool.name} has no check_cmd and no custom_installer"

    def test_all_tools_have_install_method(self):
        for tool in TOOLS:
            has_pkg = bool(tool.pkg)
            has_custom = tool.custom_installer is not None
            assert has_pkg or has_custom, f"{tool.name} has no install method"

    def test_essential_tools_exist(self):
        names = {t.name for t in TOOLS}
        for expected in ["git", "curl", "unzip"]:
            assert expected in names, f"Essential tool '{expected}' missing"
