"use client";

import { useState } from "react";

export default function DailyReportsPage() {

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
    console.log("BACKEND RESPONSE:", data);
    console.log(data);

    if (data.validation_warnings.length > 0) {

      setValidationWarnings(data.validation_warnings);

      alert(
        "⚠️ Validation Warnings:\n\n" +
        data.validation_warnings.join("\n")
      );

    } else {

      alert("✅ Daily Report Submitted");

    }

  };



  return (

    <div className="max-w-2xl space-y-6 text-black">

      <h1 className="text-3xl font-bold text-black">

        Daily Reports

      </h1>



      <form

        onSubmit={handleSubmit}

        className="space-y-4 bg-white p-6 rounded-2xl shadow-lg border border-gray-200"

      >

        <input
          type="number"
          placeholder="Work Order ID"
          className="w-full border border-gray-300 p-3 rounded text-black placeholder-gray-500 bg-white"
          value={workOrderId}
          onChange={(e) => setWorkOrderId(e.target.value)}
        />



        <input
          type="text"
          placeholder="Reported By"
          className="w-full border border-gray-300 p-3 rounded text-black placeholder-gray-500 bg-white"
          value={reportedBy}
          onChange={(e) => setReportedBy(e.target.value)}
        />



        <input
          type="number"
          placeholder="Actual Quantity"
          className="w-full border border-gray-300 p-3 rounded text-black placeholder-gray-500 bg-white"
          value={actualQty}
          onChange={(e) => setActualQty(e.target.value)}
        />



        <input
          type="number"
          placeholder="Manpower Count"
          className="w-full border border-gray-300 p-3 rounded text-black placeholder-gray-500 bg-white"
          value={manpowerCount}
          onChange={(e) => setManpowerCount(e.target.value)}
        />



        <input
          type="number"
          placeholder="Equipment Hours"
          className="w-full border border-gray-300 p-3 rounded text-black placeholder-gray-500 bg-white"
          value={equipmentHours}
          onChange={(e) => setEquipmentHours(e.target.value)}
        />



        <input
          type="number"
          placeholder="Material Consumption"
          className="w-full border border-gray-300 p-3 rounded text-black placeholder-gray-500 bg-white"
          value={materialConsumption}
          onChange={(e) => setMaterialConsumption(e.target.value)}
        />



        <input
          type="text"
          placeholder="Delay Reason"
          className="w-full border border-gray-300 p-3 rounded text-black placeholder-gray-500 bg-white"
          value={delayReason}
          onChange={(e) => setDelayReason(e.target.value)}
        />



        <input
          type="text"
          placeholder="Weather Status"
          className="w-full border border-gray-300 p-3 rounded text-black placeholder-gray-500 bg-white"
          value={weatherStatus}
          onChange={(e) => setWeatherStatus(e.target.value)}
        />



        <input
          type="number"
          placeholder="Photo Count"
          className="w-full border border-gray-300 p-3 rounded text-black placeholder-gray-500 bg-white"
          value={photoCount}
          onChange={(e) => setPhotoCount(e.target.value)}
        />



        <input
          type="text"
          placeholder="Report Status"
          className="w-full border border-gray-300 p-3 rounded text-black placeholder-gray-500 bg-white"
          value={reportStatus}
          onChange={(e) => setReportStatus(e.target.value)}
        />



        <input
          type="text"
          placeholder="Approved By"
          className="w-full border border-gray-300 p-3 rounded text-black placeholder-gray-500 bg-white"
          value={approvedBy}
          onChange={(e) => setApprovedBy(e.target.value)}
        />



        <button className="bg-blue-600 hover:bg-blue-700 transition text-white px-4 py-3 rounded-lg w-full font-semibold">

          Submit Report

        </button>

      </form>
      {/* Validation Results */}

      {validationWarnings.length > 0 && (

        <div className="bg-yellow-50 border border-yellow-300 rounded-xl p-4 mt-6">

          <h2 className="text-lg font-bold text-yellow-800 mb-2">
            Validation Results
          </h2>

          <ul className="space-y-2">

            {validationWarnings.map((warning, index) => (

              <li
                key={index}
                className="text-yellow-700 font-medium"
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