import { Check } from 'lucide-react';

interface Step {
  id: string;
  label: string;
  description?: string;
}

interface StepperProps {
  steps: Step[];
  currentStep: string;
  completedSteps: string[];
}

export function Stepper({ steps, currentStep, completedSteps }: StepperProps) {
  return (
    <div className="flex items-center gap-0">
      {steps.map((step, i) => {
        const isCompleted = completedSteps.includes(step.id);
        const isCurrent = step.id === currentStep;
        const isLast = i === steps.length - 1;

        return (
          <div key={step.id} className="flex items-center">
            <div className="flex flex-col items-center">
              <div
                className={`
                  w-8 h-8 rounded-full flex items-center justify-center text-sm font-semibold
                  transition-all duration-300
                  ${isCompleted
                    ? 'bg-indigo-600 text-white'
                    : isCurrent
                    ? 'bg-indigo-100 text-indigo-600 ring-2 ring-indigo-600 ring-offset-1'
                    : 'bg-gray-100 text-gray-400'
                  }
                `}
              >
                {isCompleted ? <Check size={14} /> : i + 1}
              </div>
              <span
                className={`text-xs mt-1 font-medium whitespace-nowrap ${
                  isCurrent ? 'text-indigo-600' : isCompleted ? 'text-gray-700' : 'text-gray-400'
                }`}
              >
                {step.label}
              </span>
            </div>
            {!isLast && (
              <div
                className={`h-0.5 w-10 mb-4 mx-1 transition-all duration-300 ${
                  isCompleted ? 'bg-indigo-600' : 'bg-gray-200'
                }`}
              />
            )}
          </div>
        );
      })}
    </div>
  );
}
