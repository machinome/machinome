// Beside vitest's default reporter: at the end of a run, how many tests were
// passed from the memo, by name, and how many ran. A memoized pass is never
// counted as a fresh run. The label is the one test/support/memo.mjs writes
// into the test's meta ("passed from the memo"; ADR-003). A test skipped with
// a note (the viewer layer without a selected bundle: "no viewer bundle
// selected"; ADR-008) is listed under its note, by name, and counted neither
// passed nor run.
import {relative} from 'node:path';

export default class MemoReporter{
  constructor(){this.memo=[];this.ran=0;this.label=null;this.skipped=new Map();}
  onTestCaseResult(testCase){
    const result=testCase.result(),state=result.state,label=testCase.meta().memo;
    const name=`${relative(process.cwd(),testCase.module.moduleId)} > ${testCase.fullName}`;
    if(label){this.label=label;this.memo.push(name);}
    else if(state==='passed'||state==='failed')this.ran++;
    else if(state==='skipped'&&result.note){
      if(!this.skipped.has(result.note))this.skipped.set(result.note,[]);
      this.skipped.get(result.note).push(name);
    }
  }
  onTestRunEnd(){
    const label=this.label??'passed from the memo';
    const lines=[`Test memo: ${this.memo.length} ${label}, ${this.ran} run`];
    for(const name of this.memo)lines.push(`  ${label}: ${name}`);
    for(const [note,names] of this.skipped){
      lines.push(`Skipped, ${note}: ${names.length}`);
      for(const name of names)lines.push(`  skipped, ${note}: ${name}`);
    }
    console.log('\n'+lines.join('\n'));
  }
}
