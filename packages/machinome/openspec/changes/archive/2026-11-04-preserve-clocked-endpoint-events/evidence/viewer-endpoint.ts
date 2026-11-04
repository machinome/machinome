import { readFileSync } from 'node:fs';
import { bindingTable } from '/home/asa/devel/machinome/machinome-viewer/machinome_viewer/widget/src/bindings';
import { loadClocked } from '/home/asa/devel/machinome/machinome-viewer/machinome_viewer/widget/src/clocked/document';
import { clockedMachine } from '/home/asa/devel/machinome/machinome-viewer/machinome_viewer/widget/src/clocked/machine';
const fixture = JSON.parse(readFileSync('/home/asa/devel/machinome/machinome/WTs/preserve-clocked-endpoint-events/packages/machinome/tests/clocked-corpus.json', 'utf8'));
const entry = fixture.machines.find((e: any) => e.name === 'EndpointRelease');
const document = entry.document;
const machine = clockedMachine(loadClocked(document, 'endpoint', bindingTable(document, 'endpoint')));
for (let i=0;i<entry.script.length;i++) {
 const step=entry.script[i];
 if (step.reset) { machine.reset(); continue; }
 const {input,...request}=step.move;
 const actual=machine.move(input,request);
 console.log(JSON.stringify({step:i, actual:actual.commits, expected:entry.requests[i].commits}));
}
