import { headers } from 'next/headers';
import { ModeSelector } from '@/components/app/mode-selector';
import { getAppConfig } from '@/lib/utils';

export default async function Page() {
  const hdrs = await headers();
  const appConfig = await getAppConfig(hdrs);

  return <ModeSelector appConfig={appConfig} />;
}
