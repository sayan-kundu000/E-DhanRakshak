import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { useNotification } from '../contexts/NotificationContext';
import { Input, Select } from '../components/UI/FormComponents';
import { Button } from '../components/UI/UI';
import { ROUTES } from '../constants';

export const Register = () => {
  const { register: registerUser } = useAuth();
  const { success, error } = useNotification();
  const [submitting, setSubmitting] = useState(false);
  const navigate = useNavigate();

  const {
    register,
    handleSubmit,
    watch,
    formState: { errors },
  } = useForm({
    defaultValues: {
      full_name: '',
      email: '',
      role: 'CITIZEN',
      password: '',
      confirmPassword: '',
    },
  });

  const password = watch('password');

  const onSubmit = async (data) => {
    setSubmitting(true);
    // Remove confirmPassword before sending to API
    const { confirmPassword, ...payload } = data;
    const result = await registerUser(payload);
    setSubmitting(false);

    if (result.success) {
      success('Account registered successfully! Please log in.');
      navigate(ROUTES.LOGIN);
    } else {
      error(result.error);
    }
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      <Input
        label="Full Name"
        error={errors.full_name?.message}
        placeholder="e.g. Aarav Kumar"
        {...register('full_name', {
          required: 'Full name is required.',
          maxLength: {
            value: 100,
            message: 'Name cannot exceed 100 characters.',
          },
        })}
      />

      <Input
        label="Email Address"
        type="email"
        error={errors.email?.message}
        placeholder="e.g. citizen@gmail.com"
        {...register('email', {
          required: 'Email address is required.',
          pattern: {
            value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
            message: 'Invalid email address formatting.',
          },
        })}
      />

      <Select
        label="System Access Role"
        error={errors.role?.message}
        options={[
          { label: 'Citizen (Public Safety Submitter)', value: 'CITIZEN' },
          { label: 'Field Officer (Incident Responder)', value: 'OFFICER' },
        ]}
        {...register('role', { required: 'Please select a profile role.' })}
      />

      <Input
        label="Password"
        type="password"
        error={errors.password?.message}
        placeholder="Minimum 6 characters"
        {...register('password', {
          required: 'Password is required.',
          minLength: {
            value: 6,
            message: 'Password must be at least 6 characters long.',
          },
        })}
      />

      <Input
        label="Confirm Password"
        type="password"
        error={errors.confirmPassword?.message}
        placeholder="Confirm new password"
        {...register('confirmPassword', {
          required: 'Please confirm your password.',
          validate: (val) => val === password || 'Passwords do not match.',
        })}
      />

      <Button type="submit" loading={submitting} className="w-full mt-2">
        Create Account
      </Button>

      <div className="text-center text-sm text-slate-500 dark:text-slate-400 mt-4 border-t border-slate-100 dark:border-slate-800 pt-4">
        <span>Already have an account? </span>
        <Link to={ROUTES.LOGIN} className="text-brand-600 dark:text-brand-400 font-semibold hover:underline">
          Sign In
        </Link>
      </div>
    </form>
  );
};
export default Register;
