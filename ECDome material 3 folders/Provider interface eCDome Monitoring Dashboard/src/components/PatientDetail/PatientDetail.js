import React from 'react';
import { useParams } from 'react-router-dom';

const PatientDetail = () => {
  const { id } = useParams();

  return (
    <div className="p-6">
      <h2 className="text-2xl font-bold mb-4">Patient Detail</h2>
      <div className="bg-white rounded-lg shadow p-4">
        <p className="text-gray-600">Patient detail for ID: {id}</p>
        <p className="text-gray-600">Patient detail functionality coming soon...</p>
      </div>
    </div>
  );
};

export default PatientDetail; 