"use client";

import { useState } from "react";

type WorkUnit = {
  id: number;
  title: string;
  baseline: number;
  unit: string;
};

export default function WorkUnitsPage() {
  const [title, setTitle] = useState("");
  const [baseline, setBaseline] = useState<number | "">("");
  const [unit, setUnit] = useState("");

  const [workUnits, setWorkUnits] = useState<WorkUnit[]>([]);
  const [editingId, setEditingId] = useState<number | null>(null);

  const resetForm = () => {
    setTitle("");
    setBaseline("");
    setUnit("");
    setEditingId(null);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    if (!title || baseline === "" || !unit) return;

    if (editingId !== null) {
      // UPDATE
      setWorkUnits(
        workUnits.map((wu) =>
          wu.id === editingId
            ? { ...wu, title, baseline: Number(baseline), unit }
            : wu
        )
      );
    } else {
      // CREATE
      setWorkUnits([
        ...workUnits,
        {
          id: Date.now(),
          title,
          baseline: Number(baseline),
          unit,
        },
      ]);
    }

    resetForm();
  };

  const handleEdit = (wu: WorkUnit) => {
    setTitle(wu.title);
    setBaseline(wu.baseline);
    setUnit(wu.unit);
    setEditingId(wu.id);
  };

  const handleDelete = (id: number) => {
    setWorkUnits(workUnits.filter((wu) => wu.id !== id));
  };

  return (
    <div className="max-w-xl space-y-6">
      <h1 className="text-2xl font-bold">
        {editingId ? "Edit Work Unit" : "Create Work Unit"}
      </h1>

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
          onChange={(e) =>
            setBaseline(e.target.value === "" ? "" : Number(e.target.value))
          }
        />

        <select
          className="w-full border p-2 rounded bg-white"
          value={unit}
          onChange={(e) => setUnit(e.target.value)}
        >
          <option value="">Select unit</option>
          <option value="m2">Square Meter (m²)</option>
          <option value="m3">Cubic Meter (m³)</option>
          <option value="ton">Ton</option>
          <option value="item">Item (Count)</option>
          <option value="hour">Hour</option>
          <option value="day">Day</option>
        </select>

        <button
          type="submit"
          className="bg-black text-white px-4 py-2 rounded"
        >
          {editingId ? "Update Work Unit" : "Save Work Unit"}
        </button>

        {editingId && (
          <button
            type="button"
            onClick={resetForm}
            className="ml-3 px-4 py-2 border rounded"
          >
            Cancel
          </button>
        )}
      </form>

      <div className="space-y-3">
        <h2 className="text-xl font-semibold">Work Units List</h2>

        {workUnits.map((wu) => (
          <div
            key={wu.id}
            className="p-3 bg-white rounded shadow flex justify-between items-center"
          >
            <div>
              <div className="font-bold">{wu.title}</div>
              <div>
                Baseline: {wu.baseline} {wu.unit}
              </div>
            </div>

            <div className="space-x-2">
              <button
                onClick={() => handleEdit(wu)}
                className="px-3 py-1 bg-blue-500 text-white rounded"
              >
                Edit
              </button>

              <button
                onClick={() => handleDelete(wu.id)}
                className="px-3 py-1 bg-red-500 text-white rounded"
              >
                Delete
              </button>
            </div>
          </div>
        ))}

        {workUnits.length === 0 && (
          <div className="text-gray-500">No work units yet.</div>
        )}
      </div>
    </div>
  );
}