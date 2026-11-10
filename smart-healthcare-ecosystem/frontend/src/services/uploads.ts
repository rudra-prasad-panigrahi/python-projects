export const MAX_DOCUMENT_SIZE_BYTES = 10 * 1024 * 1024;
export const allowedDocumentTypes = new Set(['application/pdf', 'image/jpeg', 'image/png']);
export function validateDocument(file: File): string | null {
  if (!allowedDocumentTypes.has(file.type)) return 'Choose a PDF, JPG, JPEG, or PNG file.';
  if (file.size > MAX_DOCUMENT_SIZE_BYTES) return 'Files must be 10 MB or smaller.';
  return null;
}
