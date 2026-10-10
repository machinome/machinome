# Evidence

Bench: `machinome/WTs/the-identity-test-reads-the-viewer-extras-name`,
base `9e3f2f44`, planning commit `d01c3af9`. Every run below is
`env -C <bench> PYTHONPATH=<bench> PYTHONDONTWRITEBYTECODE=1
.venv/bin/python -m pytest -q -p no:cacheprovider <target>`.

## Red, on the unmodified test

Target:
`tests/test_machinome_identity.py::MachinomeIdentityTest::test_distribution_import_command_and_extras_share_the_name`

```
>       self.assertEqual(project['optional-dependencies']['viewer'],
                         ['machinome-viewer'])
E       AssertionError: Lists differ: ['machinome-viewer>=0.8.0'] != ['machinome-viewer']
tests/test_machinome_identity.py:26: AssertionError
1 failed in 0.08s
```

## Green, after the test reads each extra's requirement name

Same target:

```
1 passed, 3 subtests passed in 0.11s
```

Targets `tests/test_machinome_identity.py tests/test_release_records.py
tests/test_kernel_extras.py`:

```
29 passed, 106 subtests passed in 2.01s
```

After this file was written, the change was archived with
`openspec archive the-identity-test-reads-the-viewer-extras-name --yes`,
`openspec validate --all` was run, and the three modules were run once more.
