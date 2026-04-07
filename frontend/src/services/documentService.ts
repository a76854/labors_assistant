import { get, post } from './request';
import type { DocumentGenerateRequest, DocumentResponse } from '../types';

export const generateDocument = async (sessionId: string, data: DocumentGenerateRequest): Promise<DocumentResponse> => {
  return post<DocumentResponse>(`/api/v1/sessions/${sessionId}/generate-document`, data);
};

export const getDocument = async (docId: string): Promise<DocumentResponse> => {
  return get<DocumentResponse>(`/api/v1/documents/${docId}`);
};

export const exportDocument = async (docId: string): Promise<{ message?: string }> => {
  return get<{ message?: string }>(`/api/v1/documents/${docId}/export`);
};
