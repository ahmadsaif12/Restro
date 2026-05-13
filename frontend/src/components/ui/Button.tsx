import React from 'react';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary';
  isLoading?: boolean;
}

export const Button: React.FC<ButtonProps> = ({
  children,
  variant = 'primary',
  isLoading,
  ...props
}) => {
  return (
    <button
      className={`btn-${variant}`}
      disabled={isLoading || props.disabled}
      {...props}
    >
      {isLoading ? <div className="spinner" /> : children}
    </button>
  );
};
