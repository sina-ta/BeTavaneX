"use client";

import { useState } from "react";
import data from "@/app/data/dashboard.json";

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

  // 🔥 SORT + FILTER
  const [sortKey, setSortKey] = useState("final_score");
  const [sortAsc, setSortAsc] = useState(true);
  const [showCritical, setShowCritical] = useState(false);

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
      setWorkUnits(
        workUnits.map((wu) =>
          wu.id === editingId
            ? { ...wu, title, baseline: Number(baseline), unit }
            : wu
        )
      );
    } else {
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

  // 🔥 FILTER
  const filteredData = showCritical
    ? data.filter((d: any) => d.alert === "🔴 Critical")
    : data;

  // 🔥 SORT
  const sortedData = [...filteredData].sort((a: any, b: any) => {
    if (sortAsc) {
      return a[sortKey] > b[sortKey] ? 1 : -1;
    } else {
      return a[sortKey] < b[sortKey] ? 1 : -1;
    }
  });

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
          <option value="m2">m²</option>
          <option value="m3">m³</option>
          <option value="ton">Ton</option>
          <option value="item">Item</option>
          <option value="hour">Hour</option>
          <option value="day">Day</option>
        </select>

        <button className="bg-black text-white px-4 py-2 rounded">
          {editingId ? "Update" : "Save"}
        </button>
      </form>

      {/* Dashboard */}
      <hr className="my-8" />

      <h2 className="text-xl font-bold">BetavanX Dashboard</h2>

      {/* 🔥 FILTER BUTTON */}
      <button
        onClick={() => setShowCritical(!showCritical)}
        className="mb-2 px-3 py-1 border rounded"
      >
        {showCritical ? "Show All" : "Show Critical Only"}
      </button>

      <table className="w-full border mt-2">
        <thead>
          <tr className="bg-gray-200 text-left">
            <th className="p-2">Task</th>
            <th className="p-2">Progress</th>

            {/* 🔥 SORT CLICK */}
            <th
              className="p-2 cursor-pointer"
              onClick={() => {
                setSortKey("final_score");
                setSortAsc(!sortAsc);
              }}
            >
              Score
            </th>

            <th className="p-2">Status</th>
          </tr>
        </thead>

        <tbody>
          {sortedData.map((item: any) => (
            <tr
              key={item.task_id}
              className={
                item.alert === "🔴 Critical"
                  ? "bg-red-100"
                  : item.alert === "🟡 Warning"
                  ? "bg-yellow-100"
                  : "bg-green-100"
              }
            >
              <td className="p-2 font-bold">Task {item.task_id}</td>
              <td className="p-2">{item.progress_percent}%</td>
              <td className="p-2">{item.final_score}</td>
              <td className="p-2">{item.alert}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}