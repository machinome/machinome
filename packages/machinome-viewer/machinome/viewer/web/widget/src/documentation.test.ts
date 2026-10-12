import { readFileSync, readdirSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { join } from 'node:path';
import ts from 'typescript';
import { describe, expect, it } from 'vitest';

const root = fileURLToPath(new URL('../../../', import.meta.url));
const docs = join(root, 'docs');
function sources(dir: string): string {
  return readdirSync(dir, { withFileTypes: true }).flatMap(entry => {
    if (entry.name.startsWith('_')) return [];
    const path = join(dir, entry.name);
    return entry.isDirectory() ? [sources(path)]
      : entry.name.endsWith('.rst') ? [readFileSync(path, 'utf8')] : [];
  }).join('\n');
}

const interfaces: Record<string, Record<string, string>> = {
  'viewer.ts': Object.fromEntries([
    'ViewerHandle', 'RunHandle', 'MachineHandle', 'ViewerOptions', 'ViewInput',
  ].map(name => [name, name])),
  'clocked/machine.ts': { ClockedMachine: 'MachineHandle' },
  'navigator.ts': { NavigatorHandle: 'NavigatorHandle', NavigatorOptions: 'NavigatorOptions' },
  'inspector.ts': { InspectorHandle: 'InspectorHandle', InspectorOptions: 'InspectorOptions' },
  'develop.ts': { DevelopmentHandle: 'DevelopmentHandle', DevelopmentOptions: 'DevelopmentOptions' },
  'drivers.ts': { TriggerHandle: 'TriggerHandle' },
};

describe('user manual public interface coverage', () => {
  for (const [filename, names] of Object.entries(interfaces)) {
    const path = fileURLToPath(new URL(filename, import.meta.url));
    const file = ts.createSourceFile(filename, readFileSync(path, 'utf8'), ts.ScriptTarget.Latest, true);
    for (const node of file.statements) {
      if (!ts.isInterfaceDeclaration(node) || !names[node.name.text]) continue;
      const documentedName = names[node.name.text];
      const visit = (members: ts.NodeArray<ts.TypeElement>, prefix: string) => {
        for (const member of members) {
          if (!member.name || !ts.isIdentifier(member.name)) continue;
          const name = `${prefix}.${member.name.text}`;
          it(`documents ${name}`, () => {
            const escaped = name.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
            expect(sources(docs)).toMatch(new RegExp(`^\\.\\. js:(?:method|attribute):: ${escaped}(?:\\(|\\s|$)`, 'm'));
          });
          if (ts.isPropertySignature(member) && member.type && ts.isTypeLiteralNode(member.type)) {
            visit(member.type.members, name);
          }
        }
      };
      visit(node.members, documentedName);
    }
  }
  for (const name of ['mount', 'mountNavigator', 'mountInspector', 'mountDevelopment']) {
    it(`documents browser entry point ${name}`, () => {
      expect(sources(docs)).toContain(`.. js:function:: MachinomeViewer.${name}(`);
    });
  }
});
