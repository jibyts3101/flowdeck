
"use client";

import LogoutButton from "./logout-button";

type TopbarProps = {
  username: string;
};

export default function Topbar({ username }: TopbarProps) {
  return (
    <header className="flex h-16 items-center justify-between border-b border-gray-200 bg-white px-8">
      <div>
        <h2 className="text-lg font-semibold text-black">
          Workspace
        </h2>
      </div>

      <div className="flex items-center gap-5">
        <div className="text-right">
          <p className="text-sm font-medium text-black">
            {username}
          </p>
          <p className="text-xs text-gray-500">
            Workspace Member
          </p>
        </div>

        <LogoutButton />
      </div>
    </header>
  );
}
