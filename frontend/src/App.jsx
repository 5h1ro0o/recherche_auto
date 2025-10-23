import React from "react";

export default function App() {
  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center p-6">
      <div className="max-w-2xl w-full bg-white shadow-lg rounded-xl p-8">
        <h1 className="text-2xl font-bold mb-4">Voiture Search — Prototype</h1>
        <p className="text-gray-600 mb-6">
          Si tu vois ce message stylé, Tailwind fonctionne correctement avec Vite.
        </p>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div className="p-4 border rounded">
            <h2 className="font-semibold">Recherche</h2>
            <p className="text-sm text-gray-500">Filtres, tri, etc.</p>
          </div>
          <div className="p-4 border rounded">
            <h2 className="font-semibold">Résultats</h2>
            <p className="text-sm text-gray-500">Liste & carte</p>
          </div>
        </div>

        <div className="mt-6 text-right">
          <button className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700">
            Démarrer
          </button>
        </div>
      </div>
    </div>
  );
}
