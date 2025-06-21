import { NextResponse } from 'next/server';
import { promises as fs } from 'fs';
import path from 'path';

export async function POST(request) {
  try {
    const { command } = await request.json();
    
    if (!command) {
      return NextResponse.json(
        { error: 'Command is required' },
        { status: 400 }
      );
    }

    const timestamp = new Date().toISOString();
    const dbPath = path.join(process.cwd(), 'db.txt');
    const logEntry = `[${timestamp}] Command: ${command}\n`;

    // Handle different command types
    switch (command.toLowerCase().trim()) {
      case 'fail':
        // Log the command first
        await fs.appendFile(dbPath, logEntry);
        
        // Log error and throw
        console.error(`❌ ERROR: Command '${command}' triggered an intentional failure`);
        await fs.appendFile(dbPath, `[${timestamp}] ERROR: Intentional failure triggered\n`);
        
        return NextResponse.json(
          { error: 'Intentional failure triggered for CI/CD testing' },
          { status: 500 }
        );

      case 'warn':
        // Log the command
        await fs.appendFile(dbPath, logEntry);
        
        // Log warning
        console.warn(`⚠️  WARNING: Command '${command}' triggered a warning`);
        await fs.appendFile(dbPath, `[${timestamp}] WARNING: Warning condition triggered\n`);
        
        return NextResponse.json({
          message: 'Command processed with warning',
          type: 'warning',
          command
        });

      default:
        // Normal operation
        await fs.appendFile(dbPath, logEntry);
        
        console.log(`✅ SUCCESS: Command '${command}' processed successfully`);
        await fs.appendFile(dbPath, `[${timestamp}] SUCCESS: Command processed successfully\n`);
        
        return NextResponse.json({
          message: 'Command processed successfully',
          type: 'success',
          command
        });
    }

  } catch (error) {
    console.error('❌ API Error:', error.message);
    
    return NextResponse.json(
      { error: 'Internal server error', details: error.message },
      { status: 500 }
    );
  }
}

export async function GET() {
  try {
    const dbPath = path.join(process.cwd(), 'db.txt');
    
    try {
      const content = await fs.readFile(dbPath, 'utf8');
      const entries = content.trim().split('\n').filter(line => line.length > 0);
      
      return NextResponse.json({
        message: 'Database contents retrieved',
        entries: entries.slice(-10), // Return last 10 entries
        total: entries.length
      });
    } catch (fileError) {
      // File doesn't exist yet
      return NextResponse.json({
        message: 'Database is empty',
        entries: [],
        total: 0
      });
    }
  } catch (error) {
    console.error('❌ GET API Error:', error.message);
    
    return NextResponse.json(
      { error: 'Failed to read database' },
      { status: 500 }
    );
  }
}
