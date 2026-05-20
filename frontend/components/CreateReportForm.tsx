"use client";

import { useState } from "react";

type Props = {
  onReportCreated: () => void;
};

export default function CreateReportForm({
  onReportCreated,
}: Props) {

  const [workOrderId, setWorkOrderId] = useState("");

  const [reportedBy, setReportedBy] = useState("");

  const [actualQty, setActualQty] = useState("");

  const [manpowerCount, setManpowerCount] = useState("");

  const [equipmentHours, setEquipmentHours] = useState("");

  const [materialConsumption, setMaterialConsumption] = useState("");

  const [delayReason, setDelayReason] = useState("");

  const [weatherStatus, setWeatherStatus] = useState("");

  const [photoCount, setPhotoCount] = useState("");

  const [reportStatus, setReportStatus] = useState("");

  const [approvedBy, setApprovedBy] = useState("");

  const [validationWarnings, setValidationWarnings] = useState<string[]>([]);

  const handleSubmit = async (e: any) => {

    e.preventDefault();

    const payload = {

      work_order_id: Number(workOrderId),

      reported_by: reportedBy,

      actual_qty: Number(actualQty),

      manpower_count: Number(manpowerCount),

      equipment_hours: Number(equipmentHours),

      material_consumption: Number(materialConsumption),

      delay_reason: delayReason,

      weather_status: weatherStatus,

      photo_count: Number(photoCount),

      report_status: reportStatus,

      approved_by: approvedBy
    };

    const res = await fetch(
      "http://127.0.0.1:8000/daily-report",
      {
        method: "POST",

        headers: {
          "Content-Type": "application/json",
        },

        body: JSON.stringify(payload),
      }
    );

    const data = await res.json();

    if (data.validation_warnings.length > 0) {

      setValidationWarnings(data.validation_warnings);

    } else {

      setValidationWarnings([]);

      alert("✅ Daily Report Submitted");
      onReportCreated();
    }
  };

  return (

    <div className="space-y-6">

      <form
        onSubmit={handleSubmit}
        className="card space-y-4"
      >

        <input
          type="number"
          placeholder="Work Order ID"
          className="input"
          value={workOrderId}
          onChange={(e) => setWorkOrderId(e.target.value)}
        />

        <input
          type="text"
          placeholder="Reported By"
          className="input"
          value={reportedBy}
          onChange={(e) => setReportedBy(e.target.value)}
        />

        <input
          type="number"
          placeholder="Actual Quantity"
          className="input"
          value={actualQty}
          onChange={(e) => setActualQty(e.target.value)}
        />

        <input
          type="number"
          placeholder="Manpower Count"
          className="input"
          value={manpowerCount}
          onChange={(e) => setManpowerCount(e.target.value)}
        />

        <input
          type="number"
          placeholder="Equipment Hours"
          className="input"
          value={equipmentHours}
          onChange={(e) => setEquipmentHours(e.target.value)}
        />

        <input
          type="number"
          placeholder="Material Consumption"
          className="input"
          value={materialConsumption}
          onChange={(e) => setMaterialConsumption(e.target.value)}
        />

        <input
          type="text"
          placeholder="Delay Reason"
          className="input"
          value={delayReason}
          onChange={(e) => setDelayReason(e.target.value)}
        />

        <input
          type="text"
          placeholder="Weather Status"
          className="input"
          value={weatherStatus}
          onChange={(e) => setWeatherStatus(e.target.value)}
        />

        <input
          type="number"
          placeholder="Photo Count"
          className="input"
          value={photoCount}
          onChange={(e) => setPhotoCount(e.target.value)}
        />

        <input
          type="text"
          placeholder="Report Status"
          className="input"
          value={reportStatus}
          onChange={(e) => setReportStatus(e.target.value)}
        />

        <input
          type="text"
          placeholder="Approved By"
          className="input"
          value={approvedBy}
          onChange={(e) => setApprovedBy(e.target.value)}
        />

        <button className="primary-button">

          Submit Report

        </button>

      </form>

      {validationWarnings.length > 0 && (

        <div className="warning-box">

          <h2 className="warning-title">
            Validation Results
          </h2>

          <ul className="space-y-2">

            {validationWarnings.map((warning, index) => (

              <li
                key={index}
                className="warning-text"
              >
                {warning}
              </li>

            ))}

          </ul>

        </div>

      )}

    </div>
  );
}