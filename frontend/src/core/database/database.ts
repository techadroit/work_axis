// import { createRxDatabase } from 'rxdb';
// import { getRxStorageDexie } from 'rxdb/plugins/storage-dexie';
// import type { RxDatabase, RxCollection } from 'rxdb';
//
// /**
//  * Chat Message Schema
//  */
// export interface ChatMessageDocument {
//   id: string;
//   message: string;
//   role: 'user' | 'assistant';
//   conversationId: string;
//   timestamp: number;
//   metadata?: Record<string, any>;
// }
//
// /**
//  * Chat Message Collection Type
//  */
// export type ChatMessageCollection = RxCollection<ChatMessageDocument>;
//
// /**
//  * User Detail Schema
//  */
// export interface UserDetailDocument {
//   userId: string;
//   timestamp: number;
// }
//
// /**
//  * User Detail Collection Type
//  */
// export type UserDetailCollection = RxCollection<UserDetailDocument>;
//
// /**
//  * Database Collections
//  */
// export interface DatabaseCollections {
//   chat_messages: ChatMessageCollection;
//   user_detail: UserDetailCollection;
// }
//
// /**
//  * Database Type
//  */
// export type AppDatabase = RxDatabase<DatabaseCollections>;
//
// /**
//  * User Detail Schema Definition
//  */
// const userDetailSchema = {
//   version: 0,
//   primaryKey: 'userId',
//   type: 'object',
//   properties: {
//     userId: {
//       type: 'string',
//       maxLength: 100,
//     },
//     timestamp: {
//       type: 'number',
//       minimum: 0,
//       maximum: 9999999999999,
//       multipleOf: 1,
//     },
//   },
//   required: ['userId', 'timestamp'],
//   indexes: ['timestamp'],
// };
//
// let dbInstance: AppDatabase | null = null;
//
// // Store database globally to persist across hot reloads
// if (typeof window !== 'undefined') {
//   (window as any).__rxdb_instance__ = (window as any).__rxdb_instance__ || null;
// }
//
// /**
//  * Initialize RxDB Database
//  */
// export const initDatabase = async (): Promise<AppDatabase> => {
//   // Check for existing instance in memory
//   if (dbInstance) {
//     console.log('[RxDB] Database already initialized in memory, returning existing instance');
//     return dbInstance;
//   }
//
//   // // Check for existing instance in window (persists across hot reloads)
//   // if (typeof window !== 'undefined' && (window as any).__rxdb_instance__) {
//   //   console.log('[RxDB] Database found in window, reusing existing instance');
//   //   dbInstance = (window as any).__rxdb_instance__;
//   //   return dbInstance;
//   // }
//
//   console.log('[RxDB] Initializing database...');
//
//   try {
//     const db = await createRxDatabase<DatabaseCollections>({
//       name: 'personal_ai_db',
//       storage: getRxStorageDexie(),
//       multiInstance: false,
//       ignoreDuplicate: true,
//     });
//
//     console.log('[RxDB] Database created successfully');
//
//     // Add collections
//     await db.addCollections({
//       user_detail: {
//         schema: userDetailSchema,
//       },
//     });
//
//     // console.log('[RxDB] Collections added successfully');
//
//     dbInstance = db;
//
//     // // Store in window for hot reload persistence
//     // if (typeof window !== 'undefined') {
//     //   (window as any).__rxdb_instance__ = db;
//     // }
//
//     return db;
//   } catch (error) {
//     console.error('[RxDB] Failed to initialize database:', error);
//
//     // Extract error details from RxError
//     const errorDetails: any = error;
//     console.error('[RxDB] Error details:', {
//       code: errorDetails?.code,
//       message: errorDetails?.message,
//       parameters: errorDetails?.parameters,
//     });
//
//     // // If DB9 error (database already exists), try to clean up and retry
//     // if (errorDetails?.code === 'DB9') {
//     //   console.log('[RxDB] DB9 error detected - database already exists. Attempting cleanup...');
//     //
//     //   try {
//     //     // Clear the window reference
//     //     if (typeof window !== 'undefined') {
//     //       (window as any).__rxdb_instance__ = null;
//     //     }
//     //
//     //     // Try to remove the database
//     //     await removeRxDatabase('personal_ai_db', getRxStorageDexie());
//     //     console.log('[RxDB] Database removed, please refresh the page to reinitialize');
//     //
//     //     throw new Error('Database was locked. Please refresh the page to continue.');
//     //   } catch (cleanupError) {
//     //     console.error('[RxDB] Failed to clean up database:', cleanupError);
//     //     throw new Error('Database initialization failed. Please clear your browser data (IndexedDB) and refresh.');
//     //   }
//     // }
//
//     throw error;
//   }
// };
//
// /**
//  * Get Database Instance
//  */
// export const getDatabase = (): AppDatabase => {
//   if (!dbInstance) {
//     throw new Error('Database not initialized. Call initDatabase() first.');
//   }
//   return dbInstance;
// };
//
// /**
//  * Close Database
//  */
// export const closeDatabase = async (): Promise<void> => {
//   if (dbInstance) {
//     await dbInstance.remove();
//     dbInstance = null;
//
//     // Clear window reference
//     if (typeof window !== 'undefined') {
//       (window as any).__rxdb_instance__ = null;
//     }
//
//     console.log('[RxDB] Database closed');
//   }
// };
//
