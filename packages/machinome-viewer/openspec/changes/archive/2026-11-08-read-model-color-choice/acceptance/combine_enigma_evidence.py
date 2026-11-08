"""Audit the explicitly authorized 44 + 19 posed-state acceptance partition."""
from hashlib import sha256
import json
from pathlib import Path
import statistics

HERE = Path(__file__).resolve().parent


def read(directory, name):
    return json.loads((HERE / directory / name).read_text())


def main():
    first = 'enigma-memory-candidate-readback'
    continuation = 'enigma-memory-candidate-continuation'
    baseline = 'enigma-memory-baseline-readback'
    oracle = read(first, 'oracle.json')
    first_rows, next_rows = (read(name, 'states.json') for name in (first, continuation))
    assert len(first_rows) == 44 and len(next_rows) == 19 and len(oracle['rows']) == 63
    first_inputs, next_inputs = (read(name, 'inputs.json') for name in (first, continuation))
    for key in ('document_sha256', 'bundle_sha256', 'oracle_sha256', 'assets', 'glass_model_identity'):
        assert first_inputs[key] == next_inputs[key], key
    assert sha256(Path(first_inputs['document']).read_bytes()).hexdigest() == first_inputs['document_sha256']
    assert sha256((HERE / first / 'oracle.json').read_bytes()).hexdigest() == first_inputs['oracle_sha256']
    terminals = {name: read(name, 'terminal.json') for name in (baseline, first, continuation)}
    assert all(not record['remaining_owned'] for record in terminals.values())
    assert terminals[baseline]['returncode'] == terminals[continuation]['returncode'] == 0
    assert 'work budget' in terminals[first]['stop_reason']
    assert next_rows[0]['complete_input_bank_supplied']
    members = []
    for index, (actual, expected) in enumerate(zip(first_rows + next_rows, oracle['rows'], strict=True)):
        assert actual['case'] == expected['case']
        assert actual['drivers'] == expected['drivers'] and len(actual['drivers']) == 11
        assert actual['colors'] == actual['expected_colors'] == expected['expected_colors_by_path']
        assert actual['expected_vector'] == expected['expected_vector_by_path']
        members.append({'oracle_index': index, 'case': actual['case'],
                        'run': first if index < 44 else continuation,
                        'index_in_run': index if index < 44 else index-44,
                        'driver_count': 11, 'verified_color_count': 26})
    lifecycle = read(continuation, 'lifecycle.json')
    assert lifecycle['same_public_body_inventory']
    assert lifecycle['model_requests_at_mount'] == lifecycle['model_requests_after_states'] == 572
    assert lifecycle['completed_model_requests'] == 572
    assert not lifecycle['errors'] and not lifecycle['failed_requests'] and not lifecycle['http_errors']
    assert lifecycle['readbacks_executed'] == lifecycle['screen_queries_executed'] == 0
    pixels = read(first, 'partial-comparison.json')
    assert pixels['changed_rgb_pixels_above_4'] == 1203
    assert pixels['alpha_bytes_unchanged'] and pixels['released_rgba_equals_dark']
    assert pixels['full_default_equals_baseline']
    calls = [call['control_ms'] for row in first_rows+next_rows for call in row['changed']]
    result = {'scope': oracle['scope'], 'oracle_sha256': first_inputs['oracle_sha256'],
              'document_sha256': first_inputs['document_sha256'], 'bundle_sha256': first_inputs['bundle_sha256'],
              'oracle_rows': 63, 'glass_paths': oracle['glass_sites'], 'verified_color_comparisons': 63*26,
              'run_membership': members, 'same_candidate_inputs_across_runs': True,
              'same_public_body_inventory': True, 'model_requests_per_context': 572,
              'additional_model_requests_on_control_changes': 0,
              'all_key_held_released_cases': [row['case'] for row in oracle['rows'][:52]],
              'phase_supply_lifecycle_cases': [row['case'] for row in oracle['rows'][52:]],
              'individual_control_ms': {'count':len(calls),'median':statistics.median(calls),'max':max(calls)},
              'row_total_ms': {'median':statistics.median([r['total_ms'] for r in first_rows+next_rows]),
                               'max':max(r['total_ms'] for r in first_rows+next_rows)},
              'representative_pixel_evidence': pixels,
              'allocations': {name:{key:terminal[key] for key in ('allocation','returncode','stop_reason',
                  'wall_seconds_including_cleanup','peak_aggregate_rss','peak_sampled_aggregate_pss','remaining_owned')}
                  for name,terminal in terminals.items()}}
    (HERE / 'enigma-combined-acceptance.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({key:result[key] for key in ('oracle_rows','verified_color_comparisons',
                     'individual_control_ms','additional_model_requests_on_control_changes')},indent=2))


if __name__ == '__main__':
    main()
