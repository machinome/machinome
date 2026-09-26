// Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
// SPDX-License-Identifier: AGPL-3.0-or-later
export const BUILD_VOLUME = [250, 210, 220] as const;

export type PrintedPiece = {
  id: string;
  name: string;
  sources: string[];
  models: string[];
  count: number;
  size: [number, number, number];
  volume: number;
  watertight: boolean;
};

function strings(value: unknown): value is string[] {
  return Array.isArray(value) && value.length > 0 && value.every((item) => typeof item === "string" && item.length > 0);
}

function size(value: unknown): value is [number, number, number] {
  return Array.isArray(value) && value.length === 3
    && value.every((item) => typeof item === "number" && Number.isFinite(item) && item >= 0);
}

export function parsePieces(value: unknown): PrintedPiece[] {
  if (!value || typeof value !== "object" || !("pieces" in value)) {
    throw new Error("This completed build has no published piece inventory.");
  }
  const inventory = (value as { pieces?: unknown }).pieces;
  if (!Array.isArray(inventory)) throw new Error("The published piece inventory is malformed.");
  const ids = new Set<string>();
  return inventory.map((item) => {
    if (!item || typeof item !== "object") throw new Error("The published piece inventory is malformed.");
    const piece = item as Partial<PrintedPiece>;
    if (
      typeof piece.id !== "string" || !/^[0-9a-f]{12}$/.test(piece.id) || ids.has(piece.id)
      || typeof piece.name !== "string" || piece.name.length === 0
      || !strings(piece.sources) || !strings(piece.models)
      || typeof piece.count !== "number" || !Number.isInteger(piece.count) || piece.count < 1
      || !size(piece.size)
      || typeof piece.volume !== "number" || !Number.isFinite(piece.volume)
      || typeof piece.watertight !== "boolean"
    ) throw new Error("The published piece inventory is malformed.");
    ids.add(piece.id);
    return {
      id: piece.id,
      name: piece.name,
      sources: [...piece.sources].sort(),
      models: [...piece.models].sort(),
      count: piece.count,
      size: piece.size,
      volume: piece.volume,
      watertight: piece.watertight,
    };
  });
}

export function canonicalModel(piece: PrintedPiece): string {
  return piece.models[0];
}

export function fitsBuildEnvelope(piece: PrintedPiece): boolean {
  const [x, y, z] = piece.size;
  const permutations = [
    [x, y, z], [x, z, y], [y, x, z], [y, z, x], [z, x, y], [z, y, x],
  ];
  return permutations.some((candidate) => candidate.every((extent, index) => extent <= BUILD_VOLUME[index]));
}

export function artifactUrl(session: string, reference: string): string {
  const path = reference.split("/").map(encodeURIComponent).join("/");
  return `/api/sessions/${encodeURIComponent(session)}/artifacts/${path}`;
}
