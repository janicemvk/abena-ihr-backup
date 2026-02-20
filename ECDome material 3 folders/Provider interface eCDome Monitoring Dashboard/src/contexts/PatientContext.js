import React, { createContext, useContext, useReducer, useEffect } from 'react';
import { patientService } from '../services/patientService';
import toast from 'react-hot-toast';

// Initial state
const initialState = {
  patients: [],
  selectedPatient: null,
  patientData: null,
  loading: false,
  error: null,
  filters: {
    status: 'all',
    riskLevel: 'all',
    sortBy: 'name'
  }
};

// Action types
const ActionTypes = {
  SET_LOADING: 'SET_LOADING',
  SET_ERROR: 'SET_ERROR',
  SET_PATIENTS: 'SET_PATIENTS',
  SET_SELECTED_PATIENT: 'SET_SELECTED_PATIENT',
  SET_PATIENT_DATA: 'SET_PATIENT_DATA',
  UPDATE_PATIENT_DATA: 'UPDATE_PATIENT_DATA',
  SET_FILTERS: 'SET_FILTERS',
  ADD_PATIENT: 'ADD_PATIENT',
  UPDATE_PATIENT: 'UPDATE_PATIENT',
  DELETE_PATIENT: 'DELETE_PATIENT'
};

// Reducer
const patientReducer = (state, action) => {
  switch (action.type) {
    case ActionTypes.SET_LOADING:
      return { ...state, loading: action.payload };
    
    case ActionTypes.SET_ERROR:
      return { ...state, error: action.payload, loading: false };
    
    case ActionTypes.SET_PATIENTS:
      return { ...state, patients: action.payload, loading: false };
    
    case ActionTypes.SET_SELECTED_PATIENT:
      return { ...state, selectedPatient: action.payload };
    
    case ActionTypes.SET_PATIENT_DATA:
      return { ...state, patientData: action.payload, loading: false };
    
    case ActionTypes.UPDATE_PATIENT_DATA:
      return {
        ...state,
        patientData: {
          ...state.patientData,
          ...action.payload
        }
      };
    
    case ActionTypes.SET_FILTERS:
      return {
        ...state,
        filters: { ...state.filters, ...action.payload }
      };
    
    case ActionTypes.ADD_PATIENT:
      return {
        ...state,
        patients: [...state.patients, action.payload]
      };
    
    case ActionTypes.UPDATE_PATIENT:
      return {
        ...state,
        patients: state.patients.map(patient =>
          patient.id === action.payload.id ? action.payload : patient
        )
      };
    
    case ActionTypes.DELETE_PATIENT:
      return {
        ...state,
        patients: state.patients.filter(patient => patient.id !== action.payload)
      };
    
    default:
      return state;
  }
};

// Context
const PatientContext = createContext();

// Provider component
export const PatientProvider = ({ children }) => {
  const [state, dispatch] = useReducer(patientReducer, initialState);

  // Actions
  const actions = {
    setLoading: (loading) => dispatch({ type: ActionTypes.SET_LOADING, payload: loading }),
    
    setError: (error) => {
      dispatch({ type: ActionTypes.SET_ERROR, payload: error });
      if (error) toast.error(error.message || 'An error occurred');
    },
    
    loadPatients: async () => {
      try {
        dispatch({ type: ActionTypes.SET_LOADING, payload: true });
        const patients = await patientService.getPatients();
        dispatch({ type: ActionTypes.SET_PATIENTS, payload: patients });
      } catch (error) {
        actions.setError(error);
      }
    },
    
    selectPatient: (patientId) => {
      dispatch({ type: ActionTypes.SET_SELECTED_PATIENT, payload: patientId });
    },
    
    loadPatientData: async (patientId) => {
      try {
        dispatch({ type: ActionTypes.SET_LOADING, payload: true });
        const patientData = await patientService.getPatientData(patientId);
        dispatch({ type: ActionTypes.SET_PATIENT_DATA, payload: patientData });
      } catch (error) {
        actions.setError(error);
      }
    },
    
    updatePatientData: (data) => {
      dispatch({ type: ActionTypes.UPDATE_PATIENT_DATA, payload: data });
    },
    
    setFilters: (filters) => {
      dispatch({ type: ActionTypes.SET_FILTERS, payload: filters });
    },
    
    addPatient: async (patientData) => {
      try {
        dispatch({ type: ActionTypes.SET_LOADING, payload: true });
        const newPatient = await patientService.createPatient(patientData);
        dispatch({ type: ActionTypes.ADD_PATIENT, payload: newPatient });
        toast.success('Patient added successfully');
      } catch (error) {
        actions.setError(error);
      }
    },
    
    updatePatient: async (patientId, patientData) => {
      try {
        dispatch({ type: ActionTypes.SET_LOADING, payload: true });
        const updatedPatient = await patientService.updatePatient(patientId, patientData);
        dispatch({ type: ActionTypes.UPDATE_PATIENT, payload: updatedPatient });
        toast.success('Patient updated successfully');
      } catch (error) {
        actions.setError(error);
      }
    },
    
    deletePatient: async (patientId) => {
      try {
        dispatch({ type: ActionTypes.SET_LOADING, payload: true });
        await patientService.deletePatient(patientId);
        dispatch({ type: ActionTypes.DELETE_PATIENT, payload: patientId });
        toast.success('Patient deleted successfully');
      } catch (error) {
        actions.setError(error);
      }
    }
  };

  // Auto-load patients on mount
  useEffect(() => {
    actions.loadPatients();
  }, []);

  // Auto-load patient data when selected patient changes
  useEffect(() => {
    if (state.selectedPatient) {
      actions.loadPatientData(state.selectedPatient);
    }
  }, [state.selectedPatient]);

  return (
    <PatientContext.Provider value={{ ...state, actions }}>
      {children}
    </PatientContext.Provider>
  );
};

// Custom hook
export const usePatient = () => {
  const context = useContext(PatientContext);
  if (!context) {
    throw new Error('usePatient must be used within a PatientProvider');
  }
  return context;
}; 