/**
 * 统一 HTTP 请求封装
 * - 基于浏览器原生 fetch
 * - 从环境变量读取 VITE_API_BASE_URL
 * - 统一处理非 2xx 响应和网络异常
 */

/** 后端 API 基础地址 */
const API_BASE_URL: string =
  import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

/** 自定义请求错误 */
export class ApiError extends Error {
  /** HTTP 状态码 */
  status: number;
  /** 后端返回的错误详情（如果可解析） */
  detail: unknown;

  constructor(status: number, message: string, detail?: unknown) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.detail = detail;
  }
}

/** 通用请求选项 */
interface RequestOptions extends Omit<RequestInit, 'method' | 'body'> {
  /** URL 查询参数 */
  params?: Record<string, string | number | boolean | undefined>;
}

/**
 * 拼接查询参数到 URL
 */
function buildUrl(
  path: string,
  params?: Record<string, string | number | boolean | undefined>,
): string {
  const url = new URL(`${API_BASE_URL}${path}`);
  if (params) {
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined) {
        url.searchParams.append(key, String(value));
      }
    });
  }
  return url.toString();
}

/**
 * 统一处理响应
 */
async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    let detail: unknown;
    try {
      detail = await response.json();
    } catch {
      // 响应体不是合法 JSON，忽略
    }
    const message =
      typeof detail === 'object' && detail !== null && 'detail' in detail
        ? String((detail as { detail: unknown }).detail)
        : `请求失败，状态码：${response.status}`;
    throw new ApiError(response.status, message, detail);
  }

  // 204 No Content 等无响应体的情况
  if (response.status === 204) {
    return undefined as T;
  }

  return response.json() as Promise<T>;
}

/**
 * GET 请求
 */
export async function get<T = unknown>(
  path: string,
  options?: RequestOptions,
): Promise<T> {
  const { params, ...fetchOptions } = options || {};
  try {
    const response = await fetch(buildUrl(path, params), {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        ...fetchOptions?.headers,
      },
      ...fetchOptions,
    });
    return handleResponse<T>(response);
  } catch (error) {
    if (error instanceof ApiError) throw error;
    throw new ApiError(0, '网络异常，无法连接到服务器', error);
  }
}

/**
 * POST 请求
 */
export async function post<T = unknown>(
  path: string,
  body?: unknown,
  options?: RequestOptions,
): Promise<T> {
  const { params, ...fetchOptions } = options || {};
  try {
    const response = await fetch(buildUrl(path, params), {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...fetchOptions?.headers,
      },
      body: body !== undefined ? JSON.stringify(body) : undefined,
      ...fetchOptions,
    });
    return handleResponse<T>(response);
  } catch (error) {
    if (error instanceof ApiError) throw error;
    throw new ApiError(0, '网络异常，无法连接到服务器', error);
  }
}
