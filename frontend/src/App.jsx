import { useState, useRef, useEffect } from 'react';

const OTP_LENGTH = 4;

export default function App() {
  const [step, setStep] = useState(1);
  const [phone, setPhone] = useState('');
  const [otp, setOtp] = useState(Array(OTP_LENGTH).fill(''));
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);

  const inputRefs = useRef([]);

  useEffect(() => {
    if (step === 2 && inputRefs.current[0]) inputRefs.current[0].focus();
  }, [step]);

  const handleSendOtp = async () => {
    if (!phone) { setError('Enter a phone number.'); return; }
    setLoading(true);
    setError('');
    try {
      const res = await fetch('http://127.0.0.1:8000/api/send-otp', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ phone }),
      });
      if (res.ok) setStep(2);
      else setError('Failed to send OTP.');
    } catch {
      setError('Connection failed. Is the backend running?');
    } finally {
      setLoading(false);
    }
  };

  const handleVerifyOtp = async () => {
    const code = otp.join('');
    if (code.length !== OTP_LENGTH) { setError('Enter the complete OTP.'); return; }
    setLoading(true);
    setError('');
    try {
      const res = await fetch('http://127.0.0.1:8000/api/verify-otp', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ phone, otp: code }),
      });
      if (res.ok) {
        setSuccess(true);
        setTimeout(() => setStep(3), 600);
      } else {
        setError('Wrong OTP. Try again.');
        setOtp(Array(OTP_LENGTH).fill(''));
        inputRefs.current[0]?.focus();
      }
    } catch {
      setError('Verification failed.');
    } finally {
      setLoading(false);
    }
  };

  const handleOtpChange = (index, value) => {
    if (!/^\d*$/.test(value)) return;
    const next = [...otp];
    next[index] = value.slice(-1);
    setOtp(next);
    if (value && index < OTP_LENGTH - 1) inputRefs.current[index + 1]?.focus();
  };

  const handleOtpKeyDown = (index, e) => {
    if (e.key === 'Backspace' && !otp[index] && index > 0) inputRefs.current[index - 1]?.focus();
    if (e.key === 'Enter') handleVerifyOtp();
  };

  const handleOtpPaste = (e) => {
    e.preventDefault();
    const paste = e.clipboardData.getData('text').replace(/\D/g, '').slice(0, OTP_LENGTH);
    if (!paste) return;
    const next = [...otp];
    paste.split('').forEach((ch, i) => { next[i] = ch; });
    setOtp(next);
    inputRefs.current[Math.min(paste.length, OTP_LENGTH - 1)]?.focus();
  };

  return (
    <div className="min-h-screen font-inter text-[#2c2c2c] flex items-center justify-center bg-[#f0efe8] px-4">
      <div className="bg-subtle fixed inset-0 pointer-events-none" />

      <div className="relative w-full max-w-sm p-8 rounded-xl card animate-scale-in">
        <div className="flex items-center justify-center gap-2.5 mb-7">
          <div className="w-7 h-7 rounded-md bg-[#6b7a5e] flex items-center justify-center text-white font-semibold text-xs tracking-tight">
            P
          </div>
          <span className="text-sm font-medium tracking-wide text-[#8a8a8a]">Phone Auth</span>
        </div>

        {step === 1 && (
          <div className="animate-slide-up" key="s1">
            <h2 className="text-xl font-semibold text-center">Welcome</h2>
            <p className="text-sm text-[#8a8a8a] text-center mt-1 mb-7">Enter your phone number</p>

            <label className="text-xs text-[#8a8a8a] uppercase tracking-wider font-medium mb-2 block">Phone Number</label>
            <div className="relative">
              <span className="absolute left-3 top-1/2 -translate-y-1/2 text-[#8a8a8a] text-sm">+91</span>
              <input
                type="text"
                placeholder="00000 00000"
                value={phone}
                onChange={(e) => setPhone(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleSendOtp()}
                className="w-full bg-[#fafaf7] border border-[#d6d4cc] rounded-lg pl-11 pr-4 py-3.5 text-[#2c2c2c] text-sm
                           focus:outline-none focus:border-[#6b7a5e]/60 focus:ring-2 focus:ring-[#6b7a5e]/10
                           transition-all duration-200 placeholder:text-[#b0aea6]"
              />
            </div>

            <button onClick={handleSendOtp} disabled={loading} className="btn-primary w-full mt-6">
              {loading ? (
                <span className="flex items-center justify-center gap-2">
                  <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                  </svg>
                  Sending...
                </span>
              ) : 'Send OTP'}
            </button>
          </div>
        )}

        {step === 2 && (
          <div className="animate-slide-up" key="s2">
            <button
              onClick={() => { setStep(1); setError(''); setOtp(Array(OTP_LENGTH).fill('')); }}
              className="text-[#8a8a8a] hover:text-[#6b7a5e] transition-colors mb-4 flex items-center gap-1.5 text-sm"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
              Back
            </button>

            <h2 className="text-xl font-semibold text-center">Verify OTP</h2>
            <p className="text-sm text-[#8a8a8a] text-center mt-1 mb-7">
              Code sent to <span className="text-[#2c2c2c] font-medium">{phone}</span>
            </p>

            <label className="text-xs text-[#8a8a8a] uppercase tracking-wider font-medium mb-3 block text-center">
              4-digit code
            </label>
            <div className="flex justify-center gap-3" onPaste={handleOtpPaste}>
              {otp.map((digit, i) => (
                <input
                  key={i}
                  ref={(el) => (inputRefs.current[i] = el)}
                  type="text"
                  inputMode="numeric"
                  maxLength={1}
                  value={digit}
                  onChange={(e) => handleOtpChange(i, e.target.value)}
                  onKeyDown={(e) => handleOtpKeyDown(i, e)}
                  className={`otp-input ${digit ? 'filled' : ''}`}
                />
              ))}
            </div>

            <button onClick={handleVerifyOtp} disabled={loading} className="btn-primary w-full mt-7">
              {loading ? (
                <span className="flex items-center justify-center gap-2">
                  <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                  </svg>
                  Verifying...
                </span>
              ) : 'Verify & Enter'}
            </button>
          </div>
        )}

        {step === 3 && (
          <div className="text-center py-2 animate-scale-in" key="s3">
            <div className="w-16 h-16 rounded-full bg-[#6b7a5e]/10 border border-[#6b7a5e]/20 flex items-center justify-center mx-auto mb-5">
              <svg className="w-8 h-8 text-[#6b7a5e] animate-check-pop" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={2.5}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
              </svg>
            </div>
            <h2 className="text-xl font-semibold mb-1">Access Granted</h2>
            <p className="text-[#8a8a8a] text-sm mb-7">Welcome to the system.</p>
            <div className="bg-[#fafaf7] border border-[#e0ded8] rounded-lg p-4 text-left space-y-2">
              <div className="flex items-center justify-between text-sm">
                <span className="text-[#8a8a8a]">Status</span>
                <span className="text-[#6b7a5e] flex items-center gap-1.5">
                  <span className="w-1.5 h-1.5 bg-[#6b7a5e] rounded-full animate-pulse" />
                  Authenticated
                </span>
              </div>
              <div className="flex items-center justify-between text-sm">
                <span className="text-[#8a8a8a]">Phone</span>
                <span className="text-[#2c2c2c]">{phone}</span>
              </div>
            </div>
            <button
              onClick={() => { setStep(1); setPhone(''); setOtp(Array(OTP_LENGTH).fill('')); setSuccess(false); }}
              className="mt-6 text-sm text-[#8a8a8a] hover:text-[#6b7a5e] transition-colors"
            >
              Sign out
            </button>
          </div>
        )}

        {error && (
          <div className="mt-4 flex items-center gap-2 bg-red-50 border border-red-200 rounded-lg px-3 py-2.5 animate-slide-up">
            <svg className="w-4 h-4 text-red-500 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <p className="text-red-600 text-sm">{error}</p>
          </div>
        )}
      </div>
    </div>
  );
}