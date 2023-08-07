from django.test.runner import DiscoverRunner


class DjangoTestsDiscoverRunner(DiscoverRunner):
    def __init__(self, **kwargs):
        self.resultclass = kwargs.get("resultclass", None)
        super().__init__(**kwargs)

    def get_resultclass(self):
        return self.resultclass or super().get_resultclass()

    def discover(self, test_labels=None, extra_tests=None, **kwargs):
        return self.build_suite(test_labels, extra_tests, **kwargs)

    def loadTestsFromNames(self, test_labels, **kwargs):
        return self.build_suite(test_labels, **kwargs)

    def run(self, tests, **kwargs):
        """
        Run the unit tests for all the test suites/cases in the provided list.

        Args:
            tests: Sequence[unittest.TestSuite | django.test.TestCase]

        Returns:
            result: TextTestResult
        """

        self.setup_test_environment()
        suite = self.build_suite(tests, **kwargs)
        databases = self.get_databases(suite)
        suite.serialized_aliases = set(
            alias for alias, serialize in databases.items() if serialize
        )
        with self.time_keeper.timed("Total database setup"):
            old_config = self.setup_databases(
                aliases=databases,
                serialized_aliases=suite.serialized_aliases,
            )
        run_failed = False
        try:
            self.run_checks(databases)
            result = self.run_suite(suite, **kwargs)
        except Exception:
            run_failed = True
            raise
        finally:
            try:
                with self.time_keeper.timed("Total database teardown"):
                    self.teardown_databases(old_config)
                self.teardown_test_environment()
            except Exception:
                # Silence teardown exceptions if an exception was raised during
                # runs to avoid shadowing it.
                if not run_failed:
                    raise
        self.time_keeper.print_results()
        return result
