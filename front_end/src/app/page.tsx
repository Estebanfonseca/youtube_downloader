// pages/index.js
'use client';
import { useState } from "react";

export default function Home() {
  const [enlace, setEnlace] = useState(''); // Estado para almacenar la URL ingresada
  const [loading, setLoading] = useState(false); // Estado para mostrar un spinner o mensaje de cargando
  const [nombreArchivo, setNombreArchivo] = useState('');

  // Función para manejar la descarga del MP3
  const handleDownload = async (e: { preventDefault: () => void; }) => {
    e.preventDefault();
    setLoading(true); 


    try {
      
      const response = await fetch('http://127.0.0.1:8000/download_mp3', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ url:enlace ,nombre_archivo: nombreArchivo === '' ? null : nombreArchivo }), // Enviamos la URL de YouTube al backend
      });
      if (!response.ok) {
        throw new Error('Error al descargar el audio');
      }

      // Obtener el archivo MP3 como un blob
      const blob = await response.blob();

      // Recuperar el nombre del archivo desde la respuesta del backend
      const contentDisposition = response.headers.get('Content-Disposition');
      const matches = /filename\*?=['"]?utf-8''([^;"\n]*)['"]?/.exec(contentDisposition? contentDisposition : '');

      // Decodificar el nombre de archivo, si está codificado en UTF-8
      const filename = matches ? decodeURIComponent(matches[1]) : nombreArchivo;
      const url = window.URL.createObjectURL(blob);

      // Crear un enlace temporal para descargar el archivo
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', filename); // Nombre del archivo descargado
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (error) {
      console.error('Error:', error);
      alert('Hubo un problema al descargar el archivo.');
    }

    setLoading(false);
  };

  return (
    <div style={{ padding: '20px' }}>
      <h1>Descargar MP3 de YouTube</h1>
      <form onSubmit={handleDownload}>
        <label htmlFor="url">Pega la url a descargar </label>
        <input
        id="url"
          type="text"
          placeholder="Introduce la URL del video de YouTube"
          value={enlace}
          onChange={(e) => setEnlace(e.target.value)}
          required
          style={{ width: '300px', padding: '10px',color:'black' }}
        />
        <br />
        <label htmlFor="nombre">Si quieres dale un nombre al archivo (opcional) </label>
        <input
        id="nombre"
          type="text"
          placeholder="Nombre de archivo"
          value={nombreArchivo}
          onChange={(e) => setNombreArchivo(e.target.value)}
          style={{ width: '300px', padding: '10px', marginTop: '10px' ,color:'black'}}
        />
        <br />
        <button type="submit" style={{ marginTop: '10px', padding: '10px 20px' ,background:'red'}}>
          {loading ? 'Descargando...' : 'Descargar MP3'}
        </button>
      </form>
    </div>
  );
}
