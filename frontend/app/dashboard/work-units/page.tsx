"use client";

import { useState } from "react";

export default function WorkUnitsPage() {
  const [title, setTitle] = useState("");
  const [baseline, setBaseline] = useState("");
  const [workUnits, setWorkUnits] = useState<
    { title: string; baseline: string }[]
> ([]);
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

  setWorkUnits([
    ...workUnits,
    { title, baseline }
  ]);

  setTitle("");
  setBaseline("");
  };

  return (
    <div className="max-w-xl space-y-6">
      <h1 className="text-2xl font-bold">Create Work Unit</h1>

      <form onSubmit={handleSubmit} className="space-y-4">
        <input
          type="text"
          placeholder="Work Title"
          className="w-full border p-2 rounded"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
        />

        <input
          type="number"
          placeholder="Baseline Quantity"
          className="w-full border p-2 rounded"
          value={baseline}
          onChange={(e) => setBaseline(e.target.value)}
        />

        <button
          type="submit"
          className="bg-black text-white px-4 py-2 rounded"
        >
          Save Work Unit
        </button>
        <div className="space-y-3">
            <h2 className="text-xl font-semibold">Work Units List</h2>

            {workUnits.map((unit, index) => (
            <div
                key={index}
                className="p-3 bg-white rounded shadow"
            >
                <div className="font-bold">{unit.title}</div>
                <div>Baseline: {unit.baseline}</div>
            </div>
            ))}
            </div>
      </form>
    </div>
  );
}