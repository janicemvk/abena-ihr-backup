/**
 * Patient Name Resolver Utility
 * Caches patient names to avoid repeated API calls
 */

import { patientService, Patient } from '@/lib/services/patientService';

interface PatientCache {
  [patientId: string]: {
    name: string;
    patient: Patient;
    timestamp: number;
  };
}

// Cache with 5 minute TTL
const CACHE_TTL = 5 * 60 * 1000;
const cache: PatientCache = {};

/**
 * Get patient name from ID, with caching
 */
export async function getPatientName(patientId: string): Promise<string> {
  // Check cache first
  const cached = cache[patientId];
  if (cached && Date.now() - cached.timestamp < CACHE_TTL) {
    return cached.name;
  }

  try {
    const response = await patientService.getById(patientId);
    if (response.success && response.patient) {
      const name = `${response.patient.first_name} ${response.patient.last_name}`.trim();
      cache[patientId] = {
        name,
        patient: response.patient,
        timestamp: Date.now(),
      };
      return name;
    }
  } catch (error) {
    console.error(`Failed to fetch patient ${patientId}:`, error);
  }

  // Return truncated ID as fallback
  return patientId.substring(0, 8) + '...';
}

/**
 * Get patient full details from ID, with caching
 */
export async function getPatient(patientId: string): Promise<Patient | null> {
  // Check cache first
  const cached = cache[patientId];
  if (cached && Date.now() - cached.timestamp < CACHE_TTL) {
    return cached.patient;
  }

  try {
    const response = await patientService.getById(patientId);
    if (response.success && response.patient) {
      const name = `${response.patient.first_name} ${response.patient.last_name}`.trim();
      cache[patientId] = {
        name,
        patient: response.patient,
        timestamp: Date.now(),
      };
      return response.patient;
    }
  } catch (error) {
    console.error(`Failed to fetch patient ${patientId}:`, error);
  }

  return null;
}

/**
 * Batch resolve multiple patient names
 */
export async function getPatientNames(patientIds: string[]): Promise<Map<string, string>> {
  const names = new Map<string, string>();
  const uncachedIds: string[] = [];

  // Check cache for all IDs
  patientIds.forEach(id => {
    const cached = cache[id];
    if (cached && Date.now() - cached.timestamp < CACHE_TTL) {
      names.set(id, cached.name);
    } else {
      uncachedIds.push(id);
    }
  });

  // Fetch uncached patients
  if (uncachedIds.length > 0) {
    try {
      // Fetch all patients and cache them
      const fetchPromises = uncachedIds.map(async (id) => {
        try {
          const response = await patientService.getById(id);
          if (response.success && response.patient) {
            const name = `${response.patient.first_name} ${response.patient.last_name}`.trim();
            cache[id] = {
              name,
              patient: response.patient,
              timestamp: Date.now(),
            };
            names.set(id, name);
          } else {
            names.set(id, id.substring(0, 8) + '...');
          }
        } catch (error) {
          console.error(`Failed to fetch patient ${id}:`, error);
          names.set(id, id.substring(0, 8) + '...');
        }
      });

      await Promise.all(fetchPromises);
    } catch (error) {
      console.error('Error batch fetching patients:', error);
    }
  }

  return names;
}

/**
 * Clear the patient cache
 */
export function clearPatientCache(): void {
  Object.keys(cache).forEach(key => delete cache[key]);
}

/**
 * Clear expired entries from cache
 */
export function clearExpiredCache(): void {
  const now = Date.now();
  Object.keys(cache).forEach(key => {
    if (now - cache[key].timestamp >= CACHE_TTL) {
      delete cache[key];
    }
  });
}

