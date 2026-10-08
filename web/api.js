export async function request(path, payload, { signal, timeoutMs = 15000 } = {}) {
  const controller = new AbortController();
  let timedOut = false;
  const cancel = () => controller.abort();
  if (signal?.aborted) cancel();
  signal?.addEventListener('abort', cancel, { once: true });
  const timer = setTimeout(() => { timedOut = true; controller.abort(); }, timeoutMs);
  const options = payload === undefined ? {} : {
    method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload),
  };
  try {
    const response = await fetch(path, { ...options, signal: controller.signal });
    let data;
    try { data = await response.json(); }
    catch (error) {
      if (controller.signal.aborted) throw error;
      throw new Error('Máy chủ trả về dữ liệu không hợp lệ. Hãy kiểm tra server Python và thử lại.');
    }
    if (!response.ok) throw new Error(data?.error || 'Máy giải đang bận. Hãy thử lại sau ít giây.');
    return data;
  } catch (error) {
    if (timedOut) throw new Error('Máy phản hồi quá lâu. Hãy kiểm tra kết nối rồi thử lại.');
    if (signal?.aborted) throw error;
    if (error instanceof TypeError) throw new Error('Không kết nối được với máy giải. Hãy kiểm tra server Python và thử lại.');
    throw error;
  } finally {
    clearTimeout(timer);
    signal?.removeEventListener('abort', cancel);
  }
}
