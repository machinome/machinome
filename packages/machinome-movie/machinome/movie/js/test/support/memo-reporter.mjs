// Beside vitest's default reporter: at the end of a run, how many tests were
// passed from the memo, by name, and how many ran. A memoized pass is never
// counted as a fresh run. The label is the one test/support/memo.mjs writes
// into the test's meta ("passed from the memo"; ADR-003).
import {relative} from 'node:path';

export default class MemoReporter{
  constructor(){this.memo=[];this.ran=0;this.label=null;}
  onTestCaseResult(testCase){
    const state=testCase.result().state,label=testCase.meta().memo;
    if(label){this.label=label;this.memo.push(`${relative(process.cwd(),testCase.module.moduleId)} > ${testCase.fullName}`);}
    else if(state==='passed'||state==='failed')this.ran++;
  }
  onTestRunEnd(){
    const label=this.label??'passed from the memo';
    const lines=[`Test memo: ${this.memo.length} ${label}, ${this.ran} run`];
    for(const name of this.memo)lines.push(`  ${label}: ${name}`);
    console.log('\n'+lines.join('\n'));
  }
}
