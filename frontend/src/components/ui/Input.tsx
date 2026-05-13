import React from 'react';

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
}

export const Input: React.FC<InputProps> = ({ label, error, ...props }) => {
  return (
    <div className="form-group">
      {label && <label className="label">{label}</label>}
      <input className="input-field" {...props} />
      {error && <p className="auth-error">{error}</p>}
    </div>
  );
};
